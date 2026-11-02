import { useEffect, useState } from "react"; // useEffect runs side effects; useState stores changing data
import { processFile } from "../lib/processingService"; // The mock processing call

// useProcessingQueue owns the shared queue and processes one file at a time
export function useProcessingQueue() {
  // state holds the queue, the current run's counts, and the finished summary
  const [state, setState] = useState({
    items: [], // every file, oldest first
    successful: 0, // successful files in the current run
    failed: 0, // failed files in the current run
    summary: null, // { successful, failed } when a run finishes, otherwise null
  });

  // enqueue adds files to the end of the queue
  function enqueue(files, kind) {
    if (files.length === 0) {
      return; // nothing to add
    }

    // Build one queue item per File object
    const newItems = files.map((file, index) => ({
      id: crypto.randomUUID(), // unique key for React and for updates
      file_name: file.name, // shown in the progress list
      kind, // "document" or "invoice" (useful for the backend later)
      file, // keep the File object for the real upload later
      status: "queued", // new files wait their turn
      error: null, // filled in if processing fails
      // Static test rule: the first file of a multi-file batch always fails
      should_fail: files.length > 1 && index === 0,
    }));

    setState((current) => {
      // A run is active if anything is waiting or processing
      const isRunning = current.items.some(
        (item) => item.status === "queued" || item.status === "processing"
      );

      return {
        items: [...current.items, ...newItems], // append the new files at the end
        successful: isRunning ? current.successful : 0, // fresh counts for a new run
        failed: isRunning ? current.failed : 0, // fresh counts for a new run
        summary: null, // hide an old summary when new work arrives
      };
    });
  }

  // finishItem records the result of the file that just finished
  function finishItem(id, status, errorMessage) {
    setState((current) => {
      // Replace only the finished item, keeping the others untouched
      const items = current.items.map((item) =>
        item.id === id ? { ...item, status, error: errorMessage ?? null } : item
      );

      // Add this result to the current run's counts
      const successful = current.successful + (status === "completed" ? 1 : 0);
      const failed = current.failed + (status === "failed" ? 1 : 0);

      // Is there still queued or processing work left?
      const hasWorkLeft = items.some(
        (item) => item.status === "queued" || item.status === "processing"
      );

      return {
        items,
        successful,
        failed,
        summary: hasWorkLeft ? current.summary : { successful, failed },
      };
    });
  }

  // Effect 1: if nothing is processing, promote the oldest queued file
  useEffect(() => {
    setState((current) => {
      // One file at a time: stop if something is already running
      const alreadyProcessing = current.items.some(
        (item) => item.status === "processing"
      );
      if (alreadyProcessing) {
        return current;
      }

      // Find the first file still waiting in line
      const next = current.items.find((item) => item.status === "queued");
      if (!next) {
        return current; // nothing waiting
      }

      // Mark that file as processing
      return {
        ...current,
        items: current.items.map((item) =>
          item.id === next.id ? { ...item, status: "processing" } : item
        ),
      };
    });
  }, [state.items]); // run whenever the list changes

  // Find the file that is currently being processed
  const processingItem = state.items.find((item) => item.status === "processing");

  // Effect 2: call the processing service for the current file
  useEffect(() => {
    if (!processingItem) {
      return; // nothing to process
    }

    let cancelled = false; // ignore a result if this effect is cleaned up

    processFile(processingItem)
      .then(() => {
        if (!cancelled) {
          finishItem(processingItem.id, "completed", null); // success result
        }
      })
      .catch((error) => {
        if (!cancelled) {
          finishItem(processingItem.id, "failed", error.message); // failure result
        }
      });

    return () => {
      cancelled = true; // stop listening to this run
    };
  }, [processingItem?.id]); // restart only when a different file starts

  // dismissSummary hides the completion popup without touching history
  function dismissSummary() {
    setState((current) => ({ ...current, summary: null }));
  }

  return {
    items: state.items,
    summary: state.summary,
    enqueue,
    dismissSummary,
  };
}
