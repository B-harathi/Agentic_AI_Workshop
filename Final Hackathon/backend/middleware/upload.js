const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure upload directory exists
const uploadDir = 'uploads/';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Generate unique filename with timestamp
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const fileExtension = path.extname(file.originalname);
    const baseName = path.basename(file.originalname, fileExtension);
    cb(null, `${baseName}-${uniqueSuffix}${fileExtension}`);
  }
});

// File filter for budget documents
const fileFilter = (req, file, cb) => {
  console.log('Uploading file:', file.originalname, 'Type:', file.mimetype);
  
  // Allowed file types for budget documents
  const allowedTypes = /xlsx|xls|pdf|docx|csv/;
  const allowedMimeTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
    'application/vnd.ms-excel', // .xls
    'application/pdf', // .pdf
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
    'text/csv', // .csv
    'application/csv'
  ];
  
  const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = allowedMimeTypes.includes(file.mimetype) || 
                   file.mimetype.includes('sheet') || 
                   file.mimetype.includes('excel') ||
                   file.mimetype.includes('pdf') ||
                   file.mimetype.includes('word') ||
                   file.mimetype.includes('csv');
  
  if (mimetype && extname) {
    console.log('✅ File type accepted:', file.originalname);
    return cb(null, true);
  } else {
    console.log('❌ File type rejected:', file.originalname, file.mimetype);
    cb(new Error('Only Excel (.xlsx, .xls), PDF (.pdf), Word (.docx), and CSV (.csv) files are allowed for budget uploads'));
  }
};

// Configure multer
const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
    files: 1 // Only allow 1 file at a time
  }
});

// Error handling middleware for multer
const handleUploadError = (error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    console.error('Multer error:', error);
    
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'File too large. Maximum size is 10MB.'
      });
    }
    
    if (error.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({
        success: false,
        error: 'Too many files. Only 1 file allowed per upload.'
      });
    }
    
    if (error.code === 'LIMIT_UNEXPECTED_FILE') {
      return res.status(400).json({
        success: false,
        error: 'Unexpected field name. Use "budget" as the field name.'
      });
    }
    
    return res.status(400).json({
      success: false,
      error: 'File upload error: ' + error.message
    });
  }
  
  if (error) {
    console.error('Upload error:', error);
    return res.status(400).json({
      success: false,
      error: error.message
    });
  }
  
  next();
};

// Cleanup old files middleware
const cleanupOldFiles = (req, res, next) => {
  try {
    const files = fs.readdirSync(uploadDir);
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    
    files.forEach(file => {
      const filePath = path.join(uploadDir, file);
      const stats = fs.statSync(filePath);
      
      if (now - stats.mtime.getTime() > maxAge) {
        fs.unlinkSync(filePath);
        console.log('🗑️ Cleaned up old file:', file);
      }
    });
  } catch (error) {
    console.warn('Warning: Could not cleanup old files:', error.message);
  }
  
  next();
};

// Export configured upload middleware
module.exports = upload;
module.exports.handleUploadError = handleUploadError;
module.exports.cleanupOldFiles = cleanupOldFiles;