import { useState } from "react"; // useState lets the component remember data that changes
import { uploadInvoice, triggerExtraction } from "../../lib/apiClient"; // real upload + extraction trigger

// UploadForm holds the documents uploader and the invoice uploader
// onProcess(files, kind) starts processing and moves to the progress screen
function UploadForm({ onProcess, isProcessing }) {
  // ---------- Documents uploader ----------
  // selectedFiles holds the chosen documents; [] is the starting value
  const [selectedFiles, setSelectedFiles] = useState([]);
  // documentsLocked = true after the user answers "No" to uploading more documents
  const [documentsLocked, setDocumentsLocked] = useState(false);
  // showUploadMorePrompt = true while the Yes/No popup is visible
  const [showUploadMorePrompt, setShowUploadMorePrompt] = useState(false);

  // handleFileChange runs whenever the user picks document files
  function handleFileChange(event) {
    // Combine the files already selected with the newly picked files
    setSelectedFiles((currentFiles) => [
      ...currentFiles, // "..." spreads (copies) the files already selected
      ...Array.from(event.target.files), // convert the new FileList to an array and add it
    ]);
  }

  // handleDocumentsSubmit runs when the documents Submit button is clicked
  function handleDocumentsSubmit(event) {
    event.preventDefault(); // Stop the browser from reloading the page

    // Do nothing when no documents are selected
    if (selectedFiles.length === 0) {
      return;
    }

    // If the section is locked, the button now says "Process"
    if (documentsLocked) {
      onProcess(selectedFiles, "document"); // send this batch to the queue
      setSelectedFiles([]); // reset: remove the stored file names
      setDocumentsLocked(false); // reset: unlock the uploader again
      return; // stop here, nothing else to do
    }

    setShowUploadMorePrompt(true); // open the Yes/No popup
  }

  // handleUploadMoreYes runs when the popup's "Yes" button is clicked
  function handleUploadMoreYes() {
    setShowUploadMorePrompt(false); // close the popup and keep the picker open
  }

  // handleUploadMoreNo runs when the popup's "No" button is clicked
  function handleUploadMoreNo() {
    setShowUploadMorePrompt(false); // close the popup
    setDocumentsLocked(true); // hide the picker and change the button label to "Process"
  }

  // ---------- Invoice uploader ----------
  // invoiceFile holds the single chosen invoice (or null when nothing is chosen)
  const [invoiceFile, setInvoiceFile] = useState(null);
  // invoiceLocked = true after one invoice has been uploaded
  const [invoiceLocked, setInvoiceLocked] = useState(false);
  // showInvoiceUploaded = true while the invoice success box is visible
  const [showInvoiceUploaded, setShowInvoiceUploaded] = useState(false);

  // handleInvoiceChange runs whenever the user picks an invoice file
  function handleInvoiceChange(event) {
    const file = event.target.files[0]; // take the first (and only) selected file
    if (!file) {
      return; // nothing selected, so do nothing
    }
    const fileName = file.name.toLowerCase(); // lowercase the name for a safe comparison
    const isAccepted = fileName.endsWith(".pdf") || fileName.endsWith(".png"); // only PDF/PNG invoices
    if (!isAccepted) {
      window.alert("Invoice not accepted. Only PDF and PNG files are allowed."); // tell the user
      setInvoiceFile(null); // discard any previously chosen invoice
      event.target.value = ""; // clear the picker so the same file can be chosen again
      return;
    }
    setInvoiceFile(file); // remember the accepted invoice
  }

  // scheduleInvoiceProcessing waits until the current invoice finishes, then processes this one
  async function scheduleInvoiceProcessing(fileName, attempt = 0) {
    if (attempt >= 10) {
      return; // stop retrying after a few attempts
    }

    try {
      const result = await triggerExtraction(fileName);
      if (result.status === "queued" && Array.isArray(result.jobs) && result.jobs.length > 0) {
        const items = result.jobs.map((job) => ({
          name: job.file_name,
          job_id: job.job_id,
        }));
        onProcess(items, "invoice");
        return;
      }

      if (result.status === "busy") {
        setTimeout(() => scheduleInvoiceProcessing(fileName, attempt + 1), 1000);
      }
    } catch (error) {
      setTimeout(() => scheduleInvoiceProcessing(fileName, attempt + 1), 1000);
    }
  }
  async function handleInvoiceSubmit(event) {
    event.preventDefault(); // Stop the browser from reloading the page

    // If the section is locked, the button now says "Process"
    if (invoiceLocked) {
      try {
        const result = await triggerExtraction(invoiceFile?.name || undefined); // ask backend to process this invoice
        if (result.status === "empty") {
          window.alert(result.message); // nothing to process
          return;
        }
        if (result.status === "busy") {
          window.alert(result.message); // already processing
          return;
        }
        // hand off all queued jobs to the queue
        const items = (result.jobs || []).map((job) => ({
          name: job.file_name,
          job_id: job.job_id,
        }));
        if (items.length === 0) {
          window.alert("No invoices to process.");
          return;
        }
        onProcess(items, "invoice"); // hand off to queue
        setInvoiceFile(null); // reset: forget the uploaded invoice
        setInvoiceLocked(false); // reset: unlock the uploader again
        setShowInvoiceUploaded(false); // reset: hide any success box still showing
      } catch (error) {
        window.alert(error.message); // show backend error
      }
      return; // stop here, nothing else to do
    }

    if (!invoiceFile) {
      return; // no invoice chosen, so nothing to "upload"
    }

    try {
      await uploadInvoice(invoiceFile); // real upload to the backend
      setShowInvoiceUploaded(true); // show the floating success box
      setInvoiceLocked(true); // hide the picker and change the button label to "Process"
      setTimeout(() => setShowInvoiceUploaded(false), 1000); // hide the box after 1 second

      // If an invoice is already processing, schedule this one to run next.
      if (isProcessing) {
        scheduleInvoiceProcessing(invoiceFile.name);
      }
    } catch (error) {
      window.alert(error.message); // show backend error (e.g. invalid type)
    }
  }

  return (
    // <> ... </> groups the two forms without adding an extra HTML element
    <>
      {/* ---------- Documents form (disabled for now) ----------
      <form
        className="upload-form"
        onSubmit={handleDocumentsSubmit} // Run the documents submit logic
      >
        ...documents uploader commented out...
      </form>
      */}
      {/* ---------- Invoice form ---------- */}
      <form
        className="invoice-form"
        onSubmit={handleInvoiceSubmit} // Run the invoice submit logic
      >
        {/* Section heading for the invoice upload */}
        <h2 className="invoice-form-title">Upload Invoice</h2>
        {/* Hide the picker once one invoice has been uploaded */}
        {!invoiceLocked && (
          <input
            className="invoice-form-input" // CSS class for styling later
            type="file" // Tells the browser this input opens a file picker
            accept=".pdf,.png" // Only show PDF and PNG files in the picker
            onChange={handleInvoiceChange} // Validate the chosen file
          />
        )}
        {/* Button label: "Submit" normally, "Process" after locking */}
        <button className="invoice-submit" type="submit">
          {invoiceLocked ? "Process" : "Submit"}
        </button>
        {/* Floating success box shown after the invoice is "uploaded" */}
        {showInvoiceUploaded && (
          <div className="upload-prompt">
            {/* Message shown inside the box */}
            <p className="upload-prompt-message">Invoice has been uploaded successfully.</p>
          </div>
        )}
      </form>
    </>
  );
}

export default UploadForm; // Export so App.jsx can import this component
