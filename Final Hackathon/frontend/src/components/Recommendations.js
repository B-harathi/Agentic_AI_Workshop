import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore,
  SwapHoriz,
  PauseCircleOutline,
  Handshake,
  CheckCircle,
  Schedule,
  TrendingUp,
  AttachMoney,
  Business,
  Warning,
  Info,
  Priority
} from '@mui/icons-material';

const dummyRecommendations = [
  {
    type: "Budget_Reallocation",
    description: "Reallocate $2,000 from Marketing to Sales Software.",
    target_savings: 2000
  },
  {
    type: "Spending_Pause",
    description: "Pause all new CRM purchases for 1 month.",
    target_savings: 1000
  }
];

const Recommendations = ({ recommendations, breaches }) => {
  const [expandedPanel, setExpandedPanel] = useState(false);
  const [implementedActions, setImplementedActions] = useState(new Set());

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const handleMarkImplemented = (actionId) => {
    setImplementedActions(prev => new Set([...prev, actionId]));
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
      case 'immediate':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  // Get impact icon
  const getImpactIcon = (impact) => {
    switch (impact?.toLowerCase()) {
      case 'high':
        return <TrendingUp color="success" />;
      case 'medium':
        return <TrendingUp color="warning" />;
      case 'low':
        return <TrendingUp color="info" />;
      default:
        return <Info />;
    }
  };

  // Group recommendations by type
  const groupedRecommendations = {
    reallocation: recommendations?.filter(r => 
      r.type === 'Budget_Reallocation' || 
      r.strategy_id?.includes('realloc') ||
      r.reallocation_options
    ) || [],
    spending_pauses: recommendations?.filter(r => 
      r.type === 'Spending_Pause' || 
      r.suggestion_id?.includes('pause') ||
      r.pause_recommendations
    ) || [],
    vendor_negotiations: recommendations?.filter(r => 
      r.type === 'Vendor_Renegotiation' || 
      r.recommendation_id?.includes('nego') ||
      r.negotiation_strategies
    ) || []
  };

  // Calculate total potential savings
  const calculateTotalSavings = () => {
    let total = 0;
    recommendations?.forEach(rec => {
      if (rec.target_savings) {
        total += parseFloat(rec.target_savings);
      }
      if (rec.expected_savings && rec.expected_savings.includes('%')) {
        const percent = parseFloat(rec.expected_savings.replace('%', ''));
        const estimatedBase = 10000;
        total += (estimatedBase * percent) / 100;
      }
    });
    return total;
  };

  const recList = recommendations && recommendations.length > 0 ? recommendations : dummyRecommendations;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        AI Recommendations
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        The Correction Recommender Agent has analyzed your budget breaches and generated 
        actionable strategies to regain control. Implement these recommendations based on priority.
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <SwapHoriz color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="primary.main">
                {groupedRecommendations.reallocation.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Reallocation Strategies
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <PauseCircleOutline color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {groupedRecommendations.spending_pauses.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Spending Pauses
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Handshake color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="info.main">
                {groupedRecommendations.vendor_negotiations.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Vendor Negotiations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AttachMoney color="success" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="success.main">
                {formatCurrency(calculateTotalSavings())}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Potential Savings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* No Recommendations Message */}
      {(!recommendations || recommendations.length === 0) && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6">
            No Recommendations Available
          </Typography>
          <Typography variant="body2">
            Track some expenses and detect budget breaches to receive AI-powered recommendations for corrective actions.
          </Typography>
        </Alert>
      )}

      {/* Budget Reallocation Strategies */}
      {groupedRecommendations.reallocation.length > 0 && (
        <Accordion 
          expanded={expandedPanel === 'reallocation'} 
          onChange={handleAccordionChange('reallocation')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <SwapHoriz color="primary" />
              <Typography variant="h6">
                Budget Reallocation Strategies ({groupedRecommendations.reallocation.length})
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {groupedRecommendations.reallocation.map((rec, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          {rec.target_breach?.department || rec.department || 'Budget Reallocation'}
                        </Typography>
                        <Chip 
                          size="small"
                          label={rec.priority || 'Medium'}
                          color={getPriorityColor(rec.priority)}
                        />
                      </Box>

                      <Typography variant="body2" paragraph>
                        {rec.recommended_action || 'Transfer funds from surplus categories to cover overage'}
                      </Typography>

                      {rec.reallocation_options && (
                        <List dense>
                          {rec.reallocation_options.slice(0, 2).map((option, idx) => (
                            <ListItem key={idx}>
                              <ListItemIcon>
                                {getImpactIcon(option.impact)}
                              </ListItemIcon>
                              <ListItemText 
                                primary={`Transfer ${formatCurrency(option.transfer_amount)}`}
                                secondary={`From: ${option.source_category} | Timeline: ${option.timeline}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      )}

                      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          <Chip size="small" label={`Required: ${formatCurrency(rec.target_breach?.required_amount || 0)}`} />
                          <Chip size="small" label="Immediate Action" color="warning" />
                        </Box>
                        <Button 
                          size="small" 
                          variant={implementedActions.has(`realloc_${index}`) ? 'contained' : 'outlined'}
                          color="success"
                          startIcon={implementedActions.has(`realloc_${index}`) ? <CheckCircle /> : null}
                          onClick={() => handleMarkImplemented(`realloc_${index}`)}
                        >
                          {implementedActions.has(`realloc_${index}`) ? 'Implemented' : 'Mark Done'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Spending Pause Suggestions */}
      {groupedRecommendations.spending_pauses.length > 0 && (
        <Accordion 
          expanded={expandedPanel === 'spending_pauses'} 
          onChange={handleAccordionChange('spending_pauses')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PauseCircleOutline color="warning" />
              <Typography variant="h6">
                Strategic Spending Pauses ({groupedRecommendations.spending_pauses.length})
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {groupedRecommendations.spending_pauses.map((rec, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          {rec.target?.department || rec.department || 'Spending Pause'}
                        </Typography>
                        <Chip 
                          size="small"
                          label={rec.target?.severity || 'Medium'}
                          color={getPriorityColor(rec.target?.severity)}
                        />
                      </Box>

                      {rec.pause_recommendations && (
                        <List dense>
                          {rec.pause_recommendations.slice(0, 2).map((pause, idx) => (
                            <ListItem key={idx}>
                              <ListItemIcon>
                                <PauseCircleOutline color="warning" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={pause.action}
                                secondary={`Duration: ${pause.duration} | Expected Savings: ${pause.expected_savings || 'TBD'}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      )}

                      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          <Chip size="small" label="Cost Reduction" />
                          <Chip size="small" label="Temporary" color="info" />
                        </Box>
                        <Button 
                          size="small" 
                          variant={implementedActions.has(`pause_${index}`) ? 'contained' : 'outlined'}
                          color="success"
                          startIcon={implementedActions.has(`pause_${index}`) ? <CheckCircle /> : null}
                          onClick={() => handleMarkImplemented(`pause_${index}`)}
                        >
                          {implementedActions.has(`pause_${index}`) ? 'Implemented' : 'Mark Done'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Vendor Renegotiation Strategies */}
      {groupedRecommendations.vendor_negotiations.length > 0 && (
        <Accordion 
          expanded={expandedPanel === 'vendor_negotiations'} 
          onChange={handleAccordionChange('vendor_negotiations')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Handshake color="info" />
              <Typography variant="h6">
                Vendor Renegotiation Strategies ({groupedRecommendations.vendor_negotiations.length})
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {groupedRecommendations.vendor_negotiations.map((rec, index) => (
                <Grid item xs={12} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          {rec.target_category || rec.department || 'Vendor Negotiation'}
                        </Typography>
                        <Chip 
                          size="small"
                          label={rec.recommended_priority || 'Medium Priority'}
                          color={getPriorityColor(rec.recommended_priority)}
                        />
                      </Box>

                      <Typography variant="body2" paragraph>
                        <strong>Goal:</strong> {rec.financial_goal || 'Reduce vendor costs through strategic negotiation'}
                      </Typography>

                      {rec.negotiation_strategies && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Negotiation Strategies:
                          </Typography>
                          <Grid container spacing={2}>
                            {rec.negotiation_strategies.slice(0, 3).map((strategy, idx) => (
                              <Grid item xs={12} md={4} key={idx}>
                                <Paper variant="outlined" sx={{ p: 2 }}>
                                  <Typography variant="subtitle2" gutterBottom>
                                    {strategy.strategy}
                                  </Typography>
                                  <Typography variant="body2" color="textSecondary" gutterBottom>
                                    {strategy.approach}
                                  </Typography>
                                  <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                                    <Chip 
                                      size="small" 
                                      label={`${strategy.success_probability} Success`}
                                      color={parseFloat(strategy.success_probability) > 70 ? 'success' : 'warning'}
                                    />
                                    <Chip 
                                      size="small" 
                                      label={`${strategy.timeline}`}
                                      variant="outlined"
                                    />
                                  </Box>
                                  <Typography variant="caption" color="success.main" sx={{ mt: 1, display: 'block' }}>
                                    Target Savings: {formatCurrency(strategy.target_savings)}
                                  </Typography>
                                </Paper>
                              </Grid>
                            ))}
                          </Grid>
                        </Box>
                      )}

                      <Box sx={{ mt: 3, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          <Chip size="small" label="Long-term Savings" />
                          <Chip size="small" label="Relationship Management" color="info" />
                        </Box>
                        <Button 
                          size="small" 
                          variant={implementedActions.has(`nego_${index}`) ? 'contained' : 'outlined'}
                          color="success"
                          startIcon={implementedActions.has(`nego_${index}`) ? <CheckCircle /> : null}
                          onClick={() => handleMarkImplemented(`nego_${index}`)}
                        >
                          {implementedActions.has(`nego_${index}`) ? 'In Progress' : 'Start Negotiation'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Implementation Timeline */}
      {recommendations && recommendations.length > 0 && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recommended Implementation Timeline
          </Typography>
          
          <Stepper orientation="vertical">
            <Step active={true}>
              <StepLabel>
                <Typography variant="subtitle1">Immediate Actions (0-24 hours)</Typography>
              </StepLabel>
              <StepContent>
                <List dense>
                  <ListItem>
                    <ListItemIcon><Warning color="error" /></ListItemIcon>
                    <ListItemText primary="Implement spending freezes for critical breaches" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><SwapHoriz color="primary" /></ListItemIcon>
                    <ListItemText primary="Execute emergency budget reallocations" />
                  </ListItem>
                </List>
              </StepContent>
            </Step>
            
            <Step active={true}>
              <StepLabel>
                <Typography variant="subtitle1">Short-term Actions (1-7 days)</Typography>
              </StepLabel>
              <StepContent>
                <List dense>
                  <ListItem>
                    <ListItemIcon><PauseCircleOutline color="warning" /></ListItemIcon>
                    <ListItemText primary="Initiate strategic spending pauses" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Schedule color="info" /></ListItemIcon>
                    <ListItemText primary="Schedule vendor negotiation meetings" />
                  </ListItem>
                </List>
              </StepContent>
            </Step>
            
            <Step active={true}>
              <StepLabel>
                <Typography variant="subtitle1">Long-term Actions (1-4 weeks)</Typography>
              </StepLabel>
              <StepContent>
                <List dense>
                  <ListItem>
                    <ListItemIcon><Handshake color="info" /></ListItemIcon>
                    <ListItemText primary="Complete vendor renegotiations" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><TrendingUp color="success" /></ListItemIcon>
                    <ListItemText primary="Monitor and adjust budget allocations" />
                  </ListItem>
                </List>
              </StepContent>
            </Step>
          </Stepper>
        </Paper>
      )}

      {/* Quick Actions */}
      {recommendations && recommendations.length > 0 && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button variant="contained" color="error" startIcon={<PauseCircleOutline />}>
              Emergency Freeze All
            </Button>
            <Button variant="contained" color="primary" startIcon={<SwapHoriz />}>
              Auto-Reallocate
            </Button>
            <Button variant="outlined" startIcon={<Handshake />}>
              Contact Vendors
            </Button>
            <Button variant="outlined" startIcon={<Schedule />}>
              Schedule Review
            </Button>
          </Box>
        </Box>
      )}

      {/* Example Recommendations */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6">AI Recommendations</Typography>
          <List>
            {recList.map((rec, idx) => (
              <ListItem key={idx}>
                <ListItemText
                  primary={rec.type.replace('_', ' ')}
                  secondary={`${rec.description} (Target savings: $${rec.target_savings})`}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Recommendations;