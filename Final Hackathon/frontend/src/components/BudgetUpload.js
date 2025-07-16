import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Description,
  TableChart,
  PictureAsPdf,
  InsertDriveFile
} from '@mui/icons-material';
import { apiService } from '../services/api';

const BudgetUpload = ({ onUploadSuccess, budgetLoaded }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                         'application/vnd.ms-excel', 
                         'application/pdf', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'text/csv'];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|pdf|docx|csv)$/i)) {
      setUploadResult({
        success: false,
        message: 'Please upload an Excel (.xlsx, .xls), PDF (.pdf), Word (.docx), or CSV (.csv) file'
      });
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      console.log('📄 Uploading budget file:', file.name);
      const result = await apiService.uploadBudget(file);
      
      setUploadResult({
        success: true,
        message: 'Budget file uploaded and processed successfully!',
        filename: file.name,
        data: result
      });

      if (onUploadSuccess) {
        onUploadSuccess(result);
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadResult({
        success: false,
        message: error.response?.data?.error || 'Failed to upload budget file',
        details: error.response?.data?.details
      });
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const getFileIcon = (filename) => {
    const ext = filename?.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'xlsx':
      case 'xls':
        return <TableChart color="success" />;
      case 'pdf':
        return <PictureAsPdf color="error" />;
      case 'docx':
        return <Description color="primary" />;
      case 'csv':
        return <InsertDriveFile color="info" />;
      default:
        return <InsertDriveFile />;
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Company Budget
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Upload your company budget file to begin monitoring expenses. 
        The Budget Policy Loader Agent will extract and structure budget rules using RAG technology.
      </Typography>

      {/* Current Status */}
      {budgetLoaded && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <strong>Budget Active:</strong> Budget file has been loaded and is ready for expense tracking.
        </Alert>
      )}

      {/* Upload Area */}
      <Paper
        sx={{
          p: 4,
          mb: 3,
          border: dragOver ? '2px dashed #1976d2' : '2px dashed #ccc',
          backgroundColor: dragOver ? '#f3f4f6' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: '#1976d2',
            backgroundColor: '#f8f9fa'
          }
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".xlsx,.xls,.pdf,.docx,.csv"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        
        <Typography variant="h6" gutterBottom>
          {dragOver ? 'Drop budget file here' : 'Upload Budget File'}
        </Typography>
        
        <Typography variant="body2" color="textSecondary" paragraph>
          Drag and drop your budget file here, or click to browse
        </Typography>

        <Typography variant="caption" color="textSecondary">
          Supported formats: Excel (.xlsx, .xls), PDF (.pdf), Word (.docx), CSV (.csv)
        </Typography>

        {!uploading && (
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<CloudUpload />}
              disabled={uploading}
            >
              Choose File
            </Button>
          </Box>
        )}
      </Paper>

      {/* Upload Progress */}
      {uploading && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Processing Budget File...
          </Typography>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="textSecondary">
            The Budget Policy Loader Agent is extracting and structuring budget rules. This may take a few moments.
          </Typography>
        </Paper>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <Alert 
          severity={uploadResult.success ? 'success' : 'error'} 
          sx={{ mb: 3 }}
          action={
            uploadResult.success && (
              <Chip 
                icon={<CheckCircle />} 
                label="Processing Complete" 
                color="success" 
                variant="outlined" 
              />
            )
          }
        >
          <Typography variant="body1">
            <strong>{uploadResult.success ? 'Success:' : 'Error:'}</strong> {uploadResult.message}
          </Typography>
          {uploadResult.filename && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {getFileIcon(uploadResult.filename)}
              <Typography variant="body2" sx={{ ml: 1 }}>
                File: {uploadResult.filename}
              </Typography>
            </Box>
          )}
          {uploadResult.details && (
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Details: {uploadResult.details}
            </Typography>
          )}
        </Alert>
      )}

      {/* Information Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mt: 3 }}>
        {/* What happens after upload */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              What Happens Next?
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Budget Rules Extracted"
                  secondary="AI agent processes your document using RAG"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Thresholds Identified"
                  secondary="Department/vendor/category limits detected"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Real-time Monitoring"
                  secondary="System ready to track expenses against budget"
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* File Requirements */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              File Requirements
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <TableChart color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Excel Files (.xlsx, .xls)"
                  secondary="Structured budget data with departments and limits"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <PictureAsPdf color="error" />
                </ListItemIcon>
                <ListItemText 
                  primary="PDF Documents (.pdf)"
                  secondary="Budget reports with tabular or text format"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Description color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Word Documents (.docx)"
                  secondary="Budget policies with spending guidelines"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <InsertDriveFile color="info" />
                </ListItemIcon>
                <ListItemText 
                  primary="CSV Files (.csv)"
                  secondary="Comma-separated budget data"
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Box>

      {/* Sample Budget Format */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Expected Budget Format
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            Your budget file should include the following information:
          </Typography>
          <Box sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1, 
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            overflow: 'auto'
          }}>
            <pre>{`Department | Category     | Monthly Limit | Annual Limit | Vendors
IT         | Software     | $20,000      | $240,000     | Microsoft, Adobe
IT         | Hardware     | $15,000      | $180,000     | Dell, HP
Marketing  | Advertising  | $25,000      | $300,000     | Google, Facebook
Operations | Supplies     | $8,000       | $96,000      | Office Depot`}</pre>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BudgetUpload;