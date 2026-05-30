import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCloudArrowUp, faCircleCheck, faFolderOpen, faFileMedical } from '@fortawesome/free-solid-svg-icons';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  loading?: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, loading = false }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: loading,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        style={
          isDragActive
            ? { borderColor: '#526D82', backgroundColor: '#9DB2BF30', transform: 'scale(1.02)' }
            : { borderColor: '#9DB2BF' }
        }
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center space-y-4">
          <div
            className="w-20 h-20 rounded-2xl flex items-center justify-center shadow-lg"
            style={{ backgroundColor: '#526D82' }}
          >
            <FontAwesomeIcon icon={faCloudArrowUp} className="w-10 h-10 text-white" />
          </div>

          {selectedFile ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 justify-center">
                <FontAwesomeIcon icon={faCircleCheck} className="w-5 h-5 text-green-500" />
                <p className="text-lg font-semibold" style={{ color: '#27374D' }}>{selectedFile.name}</p>
              </div>
              <p className="text-sm font-medium" style={{ color: '#9DB2BF' }}>
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xl font-bold flex items-center gap-2" style={{ color: '#27374D' }}>
                {isDragActive
                  ? <><FontAwesomeIcon icon={faFolderOpen} className="w-5 h-5" style={{ color: '#526D82' }} /> Drop the file here</>
                  : <><FontAwesomeIcon icon={faFileMedical} className="w-5 h-5" style={{ color: '#526D82' }} /> Drag & drop your lab report</>
                }
              </p>
              <p className="text-sm font-medium" style={{ color: '#526D82' }}>
                or click to browse
              </p>
              <div className="flex items-center justify-center gap-4 mt-4">
                {['JPG', 'PNG', 'PDF'].map((fmt) => (
                  <span
                    key={fmt}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold"
                    style={{ backgroundColor: '#526D82', color: '#ffffff' }}
                  >
                    {fmt}
                  </span>
                ))}
              </div>
              <p className="text-xs mt-2" style={{ color: '#9DB2BF' }}>
                Maximum file size: 10 MB
              </p>
            </div>
          )}
        </div>
      </div>

      {loading && (
        <div
          className="mt-6 flex items-center justify-center space-x-3 rounded-xl p-4 border"
          style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}
        >
          <div className="relative w-6 h-6">
            <div className="absolute inset-0 rounded-full border-4" style={{ borderColor: '#9DB2BF' }} />
            <div
              className="absolute inset-0 rounded-full border-4 border-t-transparent animate-spin"
              style={{ borderColor: '#526D82', borderTopColor: 'transparent' }}
            />
          </div>
          <span className="text-sm font-medium" style={{ color: '#27374D' }}>
            Uploading and processing your report…
          </span>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
