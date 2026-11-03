import UploadForm from "../components/upload/UploadForm";

// UploadPage wraps the upload form in its own page.
function UploadPage({ onProcess, isProcessing }) {
  return (
    <section className="upload-page">
      <UploadForm onProcess={onProcess} isProcessing={isProcessing} />
    </section>
  );
}

export default UploadPage;
