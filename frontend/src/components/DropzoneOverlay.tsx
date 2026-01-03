import { useDropzone } from 'react-dropzone';
import { API_BASE, API_TOKEN } from '../config';


export default function DropzoneOverlay() {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    noClick: true,
    onDrop: async (files) => {
      for (const file of files) {
        const form = new FormData();
        form.append('file', file);
        await fetch(`${API_BASE}/api/files/upload`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${API_TOKEN}` },
          body: form,
        });
      }
    },
  });

  return (
    <div
      {...getRootProps()}
      className={`absolute inset-0 ${isDragActive ? 'bg-green-200' : ''}`}
    >
      <input {...getInputProps()} />
    </div>
  );
}
