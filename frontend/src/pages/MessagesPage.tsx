import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  TextField,
  Button,
  IconButton,
  Divider,
  Badge,
  Alert,
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Fab,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Switch,
  FormControlLabel,
  Tooltip,
  Snackbar,
} from '@mui/material';
import {
  Send,
  AttachFile,
  MoreVert,
  Person,
  Business,
  Home,
  Analytics,
  TrendingUp,
  LocationOn,
  Assessment,
  SmartToy,
  AutoAwesome,
  ExpandMore,
  Speed,
  Security,
  School,
  Warning,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useSearchParams } from 'react-router-dom';
import { nvapiService, LandAnalysisResponse, ConversationContext, MessageEnhancement } from '../services/nvapiService';

interface Message {
  id: number;
  content: string;
  sender_id: number;
  receiver_id: number;
  property_id?: number;
  created_at: string;
  is_read: boolean;
  message_type?: 'inquiry' | 'response' | 'follow_up' | 'offer' | 'land_analysis' | 'deal_discussion';
  ai_enhanced?: boolean;
  land_analysis?: LandAnalysisResponse;
  enhancement_data?: MessageEnhancement;
}

interface Conversation {
  id: number;
  participant: {
    id: number;
    username: string;
    first_name?: string;
    last_name?: string;
    user_role: string;
    company_name?: string;
    avatar?: string;
  };
  property?: {
    id: number;
    title: string;
    price: number;
    location: string;
    type?: string;
    sqft?: number;
    bedrooms?: number;
    bathrooms?: number;
  };
  last_message: Message;
  unread_count: number;
  deal_status?: 'inquiry' | 'negotiating' | 'offer_pending' | 'under_contract' | 'closed' | 'cancelled';
  conversation_type?: 'general' | 'property_inquiry' | 'deal_discussion' | 'land_analysis';
}

const MessagesPage: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false);
  const [showAiSuggestions, setShowAiSuggestions] = useState(true);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [landAnalysisDialog, setLandAnalysisDialog] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<LandAnalysisResponse | null>(null);
  const [enhancementData, setEnhancementData] = useState<MessageEnhancement | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => {
    fetchConversations();
    
    // Check if we need to start a new conversation
    const agentId = searchParams.get('agent');
    const propertyId = searchParams.get('property');
    if (agentId && propertyId) {
      // TODO: Start new conversation with agent about property
    }
  }, [searchParams]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (newMessage.trim()) {
      handleMessageEnhancement(newMessage);
    } else {
      setEnhancementData(null);
      setAiSuggestions([]);
    }
  }, [newMessage]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // Enhanced mock data with deal statuses and conversation types
      const mockConversations: Conversation[] = [
        {
          id: 1,
          participant: {
            id: 2,
            username: 'sarah_agent',
            first_name: 'Sarah',
            last_name: 'Johnson',
            user_role: 'seller_agent',
            company_name: 'Premier Realty',
            avatar: '/api/placeholder/40/40'
          },
          property: {
            id: 1,
            title: 'Beautiful 3BR Home in Naperville',
            price: 425000,
            location: 'Naperville, IL',
            type: 'Single Family',
            sqft: 2200,
            bedrooms: 3,
            bathrooms: 2.5
          },
          last_message: {
            id: 1,
            content: 'Hi! I saw your interest in the Naperville property. Would you like me to run a comprehensive land analysis for this area?',
            sender_id: 2,
            receiver_id: user?.id || 1,
            property_id: 1,
            created_at: '2024-01-15T14:30:00Z',
            is_read: false,
            message_type: 'inquiry',
            ai_enhanced: true
          },
          unread_count: 1,
          deal_status: 'inquiry',
          conversation_type: 'property_inquiry'
        },
        {
          id: 2,
          participant: {
            id: 3,
            username: 'mike_agent',
            first_name: 'Mike',
            last_name: 'Davis',
            user_role: 'buyer_agent',
            company_name: 'Urban Properties',
            avatar: '/api/placeholder/40/40'
          },
          property: {
            id: 2,
            title: 'Modern 4BR House in Schaumburg',
            price: 465000,
            location: 'Schaumburg, IL',
            type: 'Single Family',
            sqft: 2800,
            bedrooms: 4,
            bathrooms: 3
          },
          last_message: {
            id: 2,
            content: 'Thanks for the property details. My client is very interested. Can we discuss deal terms?',
            sender_id: user?.id || 1,
            receiver_id: 3,
            created_at: '2024-01-14T16:45:00Z',
            is_read: true,
            message_type: 'deal_discussion'
          },
          unread_count: 0,
          deal_status: 'negotiating',
          conversation_type: 'deal_discussion'
        },
        {
          id: 3,
          participant: {
            id: 4,
            username: 'property_seller',
            first_name: 'John',
            last_name: 'Smith',
            user_role: 'seller',
            avatar: '/api/placeholder/40/40'
          },
          property: {
            id: 3,
            title: 'Investment Property in Chicago',
            price: 320000,
            location: 'Chicago, IL',
            type: 'Condo',
            sqft: 1200,
            bedrooms: 2,
            bathrooms: 2
          },
          last_message: {
            id: 3,
            content: 'I\'m interested in your investment analysis for the Chicago market. Can you provide insights?',
            sender_id: user?.id || 1,
            receiver_id: 4,
            created_at: '2024-01-13T10:20:00Z',
            is_read: true,
            message_type: 'land_analysis'
          },
          unread_count: 0,
          deal_status: 'inquiry',
          conversation_type: 'land_analysis'
        }
      ];
      
      setConversations(mockConversations);
      if (mockConversations.length > 0) {
        setSelectedConversation(mockConversations[0]);
        fetchMessages(mockConversations[0].id);
      }
    } catch (err: any) {
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId: number) => {
    try {
      // TODO: Replace with actual API call
      // Enhanced mock messages with AI features
      const mockMessages: Message[] = [
        {
          id: 1,
          content: 'Hi! I saw your interest in the Naperville property. Would you like me to run a comprehensive land analysis for this area?',
          sender_id: 2,
          receiver_id: user?.id || 1,
          property_id: 1,
          created_at: '2024-01-15T14:30:00Z',
          is_read: false,
          message_type: 'inquiry',
          ai_enhanced: true
        },
        {
          id: 2,
          content: 'Yes, I\'m very interested! Please provide a detailed analysis including safety scores, market trends, and investment potential.',
          sender_id: user?.id || 1,
          receiver_id: 2,
          property_id: 1,
          created_at: '2024-01-15T14:35:00Z',
          is_read: true,
          message_type: 'response'
        },
        {
          id: 3,
          content: 'Perfect! I\'ve generated a comprehensive land analysis for Naperville. The overall score is 87.5/100 with excellent safety ratings and strong market appreciation trends.',
          sender_id: 2,
          receiver_id: user?.id || 1,
          property_id: 1,
          created_at: '2024-01-15T14:40:00Z',
          is_read: false,
          message_type: 'land_analysis',
          ai_enhanced: true,
          land_analysis: {
            analysisId: 'analysis_1642255200000',
            location: 'Naperville, IL',
            overallScore: 87.5,
            recommendation: 'buy',
            confidenceLevel: 0.92,
            keyFactors: [
              { factor: 'Safety & Crime Rate', score: 91.2, impact: 'positive', description: 'Extremely low crime rate with excellent police response' },
              { factor: 'School Quality', score: 95.8, impact: 'positive', description: 'Top-rated school district in the state' },
              { factor: 'Market Trends', score: 84.3, impact: 'positive', description: '8.2% price appreciation over past year' },
              { factor: 'Transportation', score: 82.7, impact: 'positive', description: 'Excellent highway and train access to Chicago' }
            ],
            marketInsights: [
              'Naperville has shown 8.2% price appreciation over the past year',
              'Inventory levels are 23% below historical averages, indicating strong demand',
              'Average days on market decreased to 18 days, down from 32 days last year',
              'New construction permits increased by 15%, suggesting growing neighborhood interest'
            ],
            riskFactors: [
              'Property taxes may increase due to rising assessed values',
              'Traffic congestion during peak hours on main roads'
            ],
            opportunities: [
              'Upcoming transit expansion will improve connectivity',
              'New shopping center development planned within 2 miles'
            ],
            predictedValueChange: {
              oneYear: 6.8,
              threeYear: 18.5,
              fiveYear: 32.1
            },
            comparable_properties: [
              { address: '1234 Maple Street', price: 425000, score: 87.5, distance: 0.3 },
              { address: '5678 Oak Avenue', price: 445000, score: 91.2, distance: 0.7 }
            ]
          }
        }
      ];
      
      setMessages(mockMessages);
    } catch (err: any) {
      setError('Failed to load messages');
    }
  };

  const handleMessageEnhancement = async (message: string) => {
    if (!selectedConversation || !user) return;
    
    try {
      const conversationHistory: Array<{
        role: 'user' | 'assistant';
        content: string;
        timestamp: string;
      }> = messages.map(msg => ({
        role: msg.sender_id === user.id ? 'user' as const : 'assistant' as const,
        content: msg.content,
        timestamp: msg.created_at
      })).slice(-5); // Last 5 messages for context
      
      const context: ConversationContext = {
        propertyId: selectedConversation.property?.id,
        userId: user.id,
        userRole: user.user_role,
        conversationHistory
      };
      
      const enhancement = await nvapiService.enhanceMessage(message, context);
      setEnhancementData(enhancement);
      
      if (enhancement.suggestedResponses) {
        setAiSuggestions(enhancement.suggestedResponses);
      }
    } catch (error) {
      console.error('Error enhancing message:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      setAiAnalysisLoading(true);
      
      // Check if message should trigger land analysis
      const shouldAnalyze = enhancementData?.hasLandAnalysis && 
        /\b(analysis|analyze|score|rating|investment|market)\b/i.test(newMessage);
      
      let landAnalysis: LandAnalysisResponse | undefined;
      
      if (shouldAnalyze && user) {
        const context: ConversationContext = {
          propertyId: selectedConversation.property?.id,
          userId: user.id,
          userRole: user.user_role
        };
        
        landAnalysis = await nvapiService.generateLandAnalysisResponse(newMessage, context);
        setCurrentAnalysis(landAnalysis);
        setLandAnalysisDialog(true);
      }
      
      // Create new message
      const newMsg: Message = {
        id: Date.now(),
        content: newMessage,
        sender_id: user?.id || 1,
        receiver_id: selectedConversation.participant.id,
        property_id: selectedConversation.property?.id,
        created_at: new Date().toISOString(),
        is_read: false,
        message_type: shouldAnalyze ? 'land_analysis' : 'response',
        ai_enhanced: shouldAnalyze,
        land_analysis: landAnalysis,
        enhancement_data: enhancementData || undefined
      };

      setMessages(prev => [...prev, newMsg]);
      setNewMessage('');
      setEnhancementData(null);
      setAiSuggestions([]);
      
      // Generate AI response if appropriate
      if (shouldAnalyze) {
        setTimeout(async () => {
          try {
            const aiResponse = await nvapiService.generateConversationResponse(
              newMessage, 
              { 
                propertyId: selectedConversation.property?.id,
                userId: selectedConversation.participant.id,
                userRole: selectedConversation.participant.user_role as any
              }
            );
            
            const aiMsg: Message = {
              id: Date.now() + 1,
              content: aiResponse,
              sender_id: selectedConversation.participant.id,
              receiver_id: user?.id || 1,
              property_id: selectedConversation.property?.id,
              created_at: new Date().toISOString(),
              is_read: false,
              message_type: 'response',
              ai_enhanced: true
            };
            
            setMessages(prev => [...prev, aiMsg]);
          } catch (error) {
            console.error('Error generating AI response:', error);
          }
        }, 2000);
      }
      
      setSnackbarMessage('Message sent successfully!');
      setSnackbarOpen(true);
    } catch (err: any) {
      setError('Failed to send message');
    } finally {
      setAiAnalysisLoading(false);
    }
  };

  const handleSuggestedResponse = (suggestion: string) => {
    setNewMessage(suggestion);
    setAiSuggestions([]);
  };

  const handleRequestLandAnalysis = async () => {
    if (!selectedConversation?.property || !user) return;
    
    setAiAnalysisLoading(true);
    try {
      const context: ConversationContext = {
        propertyId: selectedConversation.property.id,
        userId: user.id,
        userRole: user.user_role
      };
      
      const analysis = await nvapiService.generateLandAnalysisResponse(
        `Please provide a comprehensive land analysis for ${selectedConversation.property.location}`,
        context
      );
      
      setCurrentAnalysis(analysis);
      setLandAnalysisDialog(true);
    } catch (error) {
      setError('Failed to generate land analysis');
    } finally {
      setAiAnalysisLoading(false);
    }
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'buyer_agent':
        return 'primary';
      case 'seller_agent':
        return 'secondary';
      case 'buyer':
        return 'info';
      case 'seller':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'buyer_agent':
        return 'Buyer Agent';
      case 'seller_agent':
        return 'Seller Agent';
      case 'buyer':
        return 'Buyer';
      case 'seller':
        return 'Seller';
      default:
        return role;
    }
  };

  const getDealStatusColor = (status?: string) => {
    switch (status) {
      case 'inquiry': return 'info';
      case 'negotiating': return 'warning';
      case 'offer_pending': return 'secondary';
      case 'under_contract': return 'success';
      case 'closed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getDealStatusLabel = (status?: string) => {
    switch (status) {
      case 'inquiry': return 'Inquiry';
      case 'negotiating': return 'Negotiating';
      case 'offer_pending': return 'Offer Pending';
      case 'under_contract': return 'Under Contract';
      case 'closed': return 'Closed';
      case 'cancelled': return 'Cancelled';
      default: return 'General';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography>Loading messages...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Messages
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Communicate with agents and clients
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Role-based Communication Rules */}
      {user && (
        <Alert severity="info" sx={{ mb: 3 }} icon={<AutoAwesome />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <SmartToy color="primary" />
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
              AI-Enhanced Messaging Active
            </Typography>
          </Box>
          {user.user_role === 'buyer' && 
            'Get AI-powered land analysis, market insights, and deal recommendations. Communicate directly with seller agents for property inquiries.'}
          {user.user_role === 'seller' && 
            'Receive AI-generated property valuations and market trends. Connect with buyer agents to discuss deals and negotiations.'}
          {user.user_role === 'buyer_agent' && 
            'Access comprehensive AI analytics for client presentations. Communicate with all parties to facilitate deals.'}
          {user.user_role === 'seller_agent' && 
            'Leverage AI insights for competitive market analysis. Guide clients through deal negotiations with data-driven recommendations.'}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ height: 'calc(100vh - 300px)' }}>
        {/* Conversations List */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ pb: 0 }}>
              <Typography variant="h6" gutterBottom>
                Conversations
              </Typography>
            </CardContent>
            <List sx={{ flexGrow: 1, overflow: 'auto' }}>
              {conversations.map((conversation) => (
                <ListItem
                  key={conversation.id}
                  button
                  selected={selectedConversation?.id === conversation.id}
                  onClick={() => {
                    setSelectedConversation(conversation);
                    fetchMessages(conversation.id);
                  }}
                  sx={{
                    borderRadius: 1,
                    mx: 1,
                    mb: 1,
                    '&.Mui-selected': {
                      backgroundColor: 'primary.light',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                      },
                    },
                  }}
                >
                  <ListItemAvatar>
                    <Badge badgeContent={conversation.unread_count} color="error">
                      <Avatar src={conversation.participant.avatar}>
                        {conversation.participant.first_name?.charAt(0) || 
                         conversation.participant.username.charAt(0).toUpperCase()}
                      </Avatar>
                    </Badge>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="subtitle2">
                          {conversation.participant.first_name} {conversation.participant.last_name}
                        </Typography>
                        <Chip
                          size="small"
                          label={getRoleLabel(conversation.participant.user_role)}
                          color={getRoleColor(conversation.participant.user_role)}
                          variant="outlined"
                        />
                        {conversation.deal_status && (
                          <Chip
                            size="small"
                            label={getDealStatusLabel(conversation.deal_status)}
                            color={getDealStatusColor(conversation.deal_status)}
                            variant="filled"
                          />
                        )}
                        {conversation.last_message.ai_enhanced && (
                          <Tooltip title="AI Enhanced Conversation">
                            <SmartToy fontSize="small" color="primary" />
                          </Tooltip>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        {conversation.participant.company_name && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            {conversation.participant.company_name}
                          </Typography>
                        )}
                        {conversation.property && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5, mb: 0.5 }}>
                            <Home fontSize="small" color="action" />
                            <Typography variant="caption" color="text.secondary">
                              {conversation.property.title}
                            </Typography>
                            {conversation.property.type && (
                              <Chip
                                size="small"
                                label={conversation.property.type}
                                variant="outlined"
                                sx={{ height: 16, fontSize: '0.6rem' }}
                              />
                            )}
                          </Box>
                        )}
                        <Typography variant="body2" sx={{ mt: 0.5 }} noWrap>
                          {conversation.last_message.content}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(conversation.last_message.created_at)}
                          </Typography>
                          {conversation.conversation_type && (
                            <Chip
                              size="small"
                              label={conversation.conversation_type.replace('_', ' ')}
                              variant="outlined"
                              sx={{ height: 16, fontSize: '0.6rem' }}
                              icon={
                                conversation.conversation_type === 'land_analysis' ? <Analytics fontSize="small" /> :
                                conversation.conversation_type === 'deal_discussion' ? <TrendingUp fontSize="small" /> :
                                <Info fontSize="small" />
                              }
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
            
            {/* AI Actions Toolbar */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', backgroundColor: 'grey.50' }}>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Tooltip title="Request AI Land Analysis">
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Analytics />}
                        onClick={handleRequestLandAnalysis}
                        disabled={aiAnalysisLoading || !selectedConversation?.property}
                      >
                        Land Analysis
                      </Button>
                    </Tooltip>
                    <Tooltip title="Get Market Insights">
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<TrendingUp />}
                        disabled={aiAnalysisLoading}
                      >
                        Market Trends
                      </Button>
                    </Tooltip>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={showAiSuggestions}
                          onChange={(e) => setShowAiSuggestions(e.target.checked)}
                          size="small"
                        />
                      }
                      label={
                        <Typography variant="caption">
                          AI Suggestions
                        </Typography>
                      }
                      sx={{ ml: 'auto' }}
                    />
                  </Box>
                  {aiAnalysisLoading && (
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress />
                      <Typography variant="caption" color="text.secondary">
                        Generating AI analysis...
                      </Typography>
                    </Box>
                  )}
                </Box>
          </Card>
        </Grid>

        {/* Messages Area */}
        <Grid item xs={12} md={8}>
          {selectedConversation ? (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* Chat Header */}
              <CardContent sx={{ pb: 1, borderBottom: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar src={selectedConversation.participant.avatar}>
                      {selectedConversation.participant.first_name?.charAt(0) || 
                       selectedConversation.participant.username.charAt(0).toUpperCase()}
                    </Avatar>
                    <Box>
                      <Typography variant="h6">
                        {selectedConversation.participant.first_name} {selectedConversation.participant.last_name}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          size="small"
                          label={getRoleLabel(selectedConversation.participant.user_role)}
                          color={getRoleColor(selectedConversation.participant.user_role)}
                          variant="outlined"
                        />
                        {selectedConversation.participant.company_name && (
                          <Typography variant="body2" color="text.secondary">
                            • {selectedConversation.participant.company_name}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                  <IconButton>
                    <MoreVert />
                  </IconButton>
                </Box>
                
                {/* Enhanced Property Info */}
                {selectedConversation.property && (
                  <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Home color="primary" />
                      <Typography variant="subtitle2">
                        {selectedConversation.property.title}
                      </Typography>
                      {selectedConversation.deal_status && (
                        <Chip
                          size="small"
                          label={getDealStatusLabel(selectedConversation.deal_status)}
                          color={getDealStatusColor(selectedConversation.deal_status)}
                          variant="filled"
                        />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      ${selectedConversation.property.price.toLocaleString()} • {selectedConversation.property.location}
                    </Typography>
                    {selectedConversation.property.sqft && (
                      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Typography variant="caption" color="text.secondary">
                          {selectedConversation.property.sqft.toLocaleString()} sq ft
                        </Typography>
                        {selectedConversation.property.bedrooms && (
                          <Typography variant="caption" color="text.secondary">
                            {selectedConversation.property.bedrooms} bed
                          </Typography>
                        )}
                        {selectedConversation.property.bathrooms && (
                          <Typography variant="caption" color="text.secondary">
                            {selectedConversation.property.bathrooms} bath
                          </Typography>
                        )}
                      </Box>
                    )}
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Button size="small" startIcon={<Analytics />} onClick={handleRequestLandAnalysis}>
                        AI Analysis
                      </Button>
                      <Button size="small" startIcon={<TrendingUp />}>
                        Market Data
                      </Button>
                    </Box>
                  </Box>
                )}
              </CardContent>

              {/* Enhanced Messages List */}
              <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: message.sender_id === user?.id ? 'flex-end' : 'flex-start',
                        mb: 2,
                      }}
                    >
                      <Box sx={{ maxWidth: '75%' }}>
                        {/* AI Enhancement Indicator */}
                        {message.ai_enhanced && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, justifyContent: message.sender_id === user?.id ? 'flex-end' : 'flex-start' }}>
                            <SmartToy fontSize="small" color="primary" />
                            <Typography variant="caption" color="primary">
                              AI Enhanced
                            </Typography>
                          </Box>
                        )}
                        
                        {/* Message Bubble */}
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            backgroundColor: message.sender_id === user?.id ? 'primary.main' : 'grey.100',
                            color: message.sender_id === user?.id ? 'white' : 'text.primary',
                          }}
                        >
                          <Typography variant="body1">
                            {message.content}
                          </Typography>
                          
                          {/* Land Analysis Preview */}
                          {message.land_analysis && (
                            <Box sx={{ mt: 2, p: 1, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                <Analytics fontSize="small" />
                                <Typography variant="subtitle2">
                                  Land Analysis: {message.land_analysis.location}
                                </Typography>
                                <Chip
                                  size="small"
                                  label={`Score: ${message.land_analysis.overallScore}/100`}
                                  color={message.land_analysis.overallScore >= 80 ? 'success' : message.land_analysis.overallScore >= 60 ? 'warning' : 'error'}
                                  variant="filled"
                                />
                              </Box>
                              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                                Recommendation: <strong>{message.land_analysis.recommendation.toUpperCase()}</strong>
                              </Typography>
                              <Button
                                size="small"
                                variant="outlined"
                                sx={{ color: 'inherit', borderColor: 'rgba(255,255,255,0.5)' }}
                                onClick={() => {
                                  setCurrentAnalysis(message.land_analysis!);
                                  setLandAnalysisDialog(true);
                                }}
                              >
                                View Full Analysis
                              </Button>
                            </Box>
                          )}
                          
                          <Typography
                            variant="caption"
                            sx={{
                              display: 'block',
                              mt: 1,
                              opacity: 0.8,
                              textAlign: 'right',
                            }}
                          >
                            {formatTime(message.created_at)}
                            {message.message_type && message.message_type !== 'response' && (
                              <Chip
                                size="small"
                                label={message.message_type.replace('_', ' ')}
                                sx={{ ml: 1, height: 16, fontSize: '0.6rem' }}
                                variant="outlined"
                              />
                            )}
                          </Typography>
                        </Paper>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
              </Box>

              {/* Enhanced Message Input */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                {/* AI Suggestions */}
                {showAiSuggestions && aiSuggestions.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                      <AutoAwesome fontSize="small" />
                      AI Suggestions:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {aiSuggestions.map((suggestion, index) => (
                        <Chip
                          key={index}
                          label={suggestion}
                          size="small"
                          variant="outlined"
                          onClick={() => handleSuggestedResponse(suggestion)}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
                
                {/* Enhancement Indicators */}
                {enhancementData && (
                  <Box sx={{ mb: 2, p: 1, backgroundColor: 'info.light', borderRadius: 1, opacity: 0.8 }}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                      {enhancementData.hasLandAnalysis && (
                        <Chip
                          size="small"
                          icon={<Analytics />}
                          label="Land Analysis Available"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {enhancementData.hasPriceAnalysis && (
                        <Chip
                          size="small"
                          icon={<TrendingUp />}
                          label="Price Analysis Available"
                          color="secondary"
                          variant="outlined"
                        />
                      )}
                      {enhancementData.hasMarketTrends && (
                        <Chip
                          size="small"
                          icon={<Assessment />}
                          label="Market Trends Available"
                          color="success"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={3}
                    placeholder="Type your message... (Try mentioning location, analysis, or market trends for AI insights)"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    InputProps={{
                      endAdornment: enhancementData && (
                        <Tooltip title="AI enhancements detected">
                          <SmartToy color="primary" fontSize="small" />
                        </Tooltip>
                      )
                    }}
                  />
                  <Tooltip title="Attach File">
                    <IconButton color="primary">
                      <AttachFile />
                    </IconButton>
                  </Tooltip>
                  {enhancementData?.hasLandAnalysis && (
                    <Tooltip title="Generate Land Analysis">
                      <IconButton color="secondary" onClick={handleRequestLandAnalysis}>
                        <Analytics />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Button
                    variant="contained"
                    endIcon={aiAnalysisLoading ? <SmartToy /> : <Send />}
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim() || aiAnalysisLoading}
                  >
                    {aiAnalysisLoading ? 'Analyzing...' : 'Send'}
                  </Button>
                </Box>
              </Box>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary">
                  Select a conversation to start messaging
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
      
      {/* Land Analysis Dialog */}
      <Dialog
        open={landAnalysisDialog}
        onClose={() => setLandAnalysisDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Analytics color="primary" />
          Land Analysis Report
          {currentAnalysis && (
            <Chip
              label={`Score: ${currentAnalysis.overallScore}/100`}
              color={currentAnalysis.overallScore >= 80 ? 'success' : currentAnalysis.overallScore >= 60 ? 'warning' : 'error'}
              variant="filled"
            />
          )}
        </DialogTitle>
        <DialogContent>
          {currentAnalysis && (
            <Box>
              {/* Location and Recommendation */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <LocationOn color="primary" />
                  <Typography variant="h6">{currentAnalysis.location}</Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                  <Chip
                    label={`Recommendation: ${currentAnalysis.recommendation.toUpperCase()}`}
                    color={currentAnalysis.recommendation === 'buy' ? 'success' : currentAnalysis.recommendation === 'hold' ? 'warning' : 'error'}
                    variant="filled"
                    size="medium"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {(currentAnalysis.confidenceLevel * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
              
              {/* Key Factors */}
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Assessment color="primary" />
                    Key Factors
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {currentAnalysis.keyFactors.map((factor, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <Paper sx={{ p: 2, height: '100%' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            {factor.impact === 'positive' ? (
                              <CheckCircle color="success" fontSize="small" />
                            ) : factor.impact === 'negative' ? (
                              <Warning color="error" fontSize="small" />
                            ) : (
                              <Info color="info" fontSize="small" />
                            )}
                            <Typography variant="subtitle2">{factor.factor}</Typography>
                          </Box>
                          <Typography variant="h6" color={factor.impact === 'positive' ? 'success.main' : factor.impact === 'negative' ? 'error.main' : 'info.main'}>
                            {factor.score}/100
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {factor.description}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              {/* Market Insights */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUp color="secondary" />
                    Market Insights
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {currentAnalysis.marketInsights.map((insight, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={insight} />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
              
              {/* Predicted Value Changes */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Speed color="info" />
                    Value Predictions
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color={currentAnalysis.predictedValueChange.oneYear >= 0 ? 'success.main' : 'error.main'}>
                          {currentAnalysis.predictedValueChange.oneYear >= 0 ? '+' : ''}{currentAnalysis.predictedValueChange.oneYear}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          1 Year
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color={currentAnalysis.predictedValueChange.threeYear >= 0 ? 'success.main' : 'error.main'}>
                          {currentAnalysis.predictedValueChange.threeYear >= 0 ? '+' : ''}{currentAnalysis.predictedValueChange.threeYear}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          3 Years
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color={currentAnalysis.predictedValueChange.fiveYear >= 0 ? 'success.main' : 'error.main'}>
                          {currentAnalysis.predictedValueChange.fiveYear >= 0 ? '+' : ''}{currentAnalysis.predictedValueChange.fiveYear}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          5 Years
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              {/* Comparable Properties */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Home color="warning" />
                    Comparable Properties
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {currentAnalysis.comparable_properties.map((comp, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={comp.address}
                          secondary={
                            <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                              <Typography variant="body2" color="text.secondary">
                                ${comp.price.toLocaleString()}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Score: {comp.score}/100
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {comp.distance} miles away
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLandAnalysisDialog(false)}>Close</Button>
          <Button variant="contained" onClick={() => {
            if (currentAnalysis) {
              setNewMessage(`Based on the AI analysis for ${currentAnalysis.location}, the property scores ${currentAnalysis.overallScore}/100 with a ${currentAnalysis.recommendation.toUpperCase()} recommendation. Key highlights include excellent safety scores and strong market trends.`);
            }
            setLandAnalysisDialog(false);
          }}>
            Use in Message
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default MessagesPage;
