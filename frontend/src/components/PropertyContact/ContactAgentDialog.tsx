import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Avatar,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import { Send, Close } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

interface Agent {
  id: number;
  first_name?: string;
  last_name?: string;
  username: string;
  email?: string;
  phone?: string;
  company_name?: string;
  avatar?: string;
  user_role?: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
}

interface Property {
  id: number;
  title: string;
  price: number;
  location: {
    address: string;
    city: string;
    state: string;
  };
}

interface ContactAgentDialogProps {
  open: boolean;
  onClose: () => void;
  agent: Agent;
  property: Property;
  onSuccess?: () => void;
}

const ContactAgentDialog: React.FC<ContactAgentDialogProps> = ({
  open,
  onClose,
  agent,
  property,
  onSuccess
}) => {
  const { user } = useAuth();
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('inquiry');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  React.useEffect(() => {
    if (open && property) {
      // Set default subject based on property
      setSubject(`Inquiry about ${property.title}`);
      // Set default message
      setMessage(`Hi ${agent.first_name || agent.username},

I'm interested in learning more about the property at ${property.location.address}, ${property.location.city}, ${property.location.state}.

Could you please provide more information or schedule a viewing?

Thank you!`);
    }
  }, [open, property, agent]);

  const handleSubmit = async () => {
    if (!subject.trim() || !message.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // TODO: Replace with actual API call
      // For now, simulate the API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock API call to send message
      const messageData = {
        recipient_id: agent.id,
        property_listing_id: property.id,
        subject: subject,
        content: message,
        message_type: messageType
      };

      console.log('Sending message:', messageData);
      
      // Show success and close dialog
      if (onSuccess) {
        onSuccess();
      }
      
      onClose();
      
      // Reset form
      setSubject('');
      setMessage('');
      setMessageType('inquiry');
      
    } catch (err: any) {
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canContact = () => {
    if (!user) return false;
    
    // Role-based validation with proper agent routing
    if (user.user_role === 'buyer') {
      // Buyers can contact seller agents directly
      if (agent.user_role === 'seller_agent' || !agent.user_role) {
        // If agent role is not specified, assume it's a seller agent for property listings
        return true;
      }
      // If trying to contact a seller, suggest going through seller agent
      if (agent.user_role === 'seller') {
        setError('As a buyer, you should contact the seller through their listing agent. Please find the listing agent for this property.');
        return false;
      }
      return true; // Default allow for buyers to contact agents
    } else if (user.user_role === 'seller') {
      // Sellers should work through their assigned seller agent
      setError('As a seller, please work with your assigned seller agent to handle buyer communications.');
      return false;
    } else if (user.user_role.includes('agent')) {
      // Agents can contact anyone
      return true;
    }
    
    return false;
  };

  const getRoleMessage = () => {
    if (!user) return '';
    
    if (user.user_role === 'seller') {
      return 'As a seller, you should work with a buyer agent to contact other agents. This helps ensure proper representation and communication.';
    }
    
    return '';
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Contact Agent</Typography>
          <Button onClick={onClose} color="inherit">
            <Close />
          </Button>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Agent Info */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
          <Avatar
            src={agent.avatar}
            alt={`${agent.first_name} ${agent.last_name}`}
            sx={{ width: 60, height: 60, mr: 2 }}
          />
          <Box>
            <Typography variant="h6">
              {agent.first_name} {agent.last_name}
            </Typography>
            {agent.company_name && (
              <Typography variant="body2" color="text.secondary">
                {agent.company_name}
              </Typography>
            )}
            {agent.email && (
              <Typography variant="body2" color="text.secondary">
                {agent.email}
              </Typography>
            )}
            {agent.phone && (
              <Typography variant="body2" color="text.secondary">
                {agent.phone}
              </Typography>
            )}
          </Box>
        </Box>

        {/* Property Info */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'primary.light', borderRadius: 1, color: 'primary.contrastText' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
            {property.title}
          </Typography>
          <Typography variant="body2">
            {property.location.address}, {property.location.city}, {property.location.state}
          </Typography>
          <Typography variant="h6" sx={{ mt: 1 }}>
            {formatPrice(property.price)}
          </Typography>
        </Box>

        {/* Role-based validation */}
        {!canContact() && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {getRoleMessage()}
          </Alert>
        )}

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {canContact() && (
          <>
            {/* Message Type */}
            <FormControl fullWidth margin="normal">
              <InputLabel>Message Type</InputLabel>
              <Select
                value={messageType}
                label="Message Type"
                onChange={(e) => setMessageType(e.target.value)}
              >
                <MenuItem value="inquiry">General Inquiry</MenuItem>
                <MenuItem value="viewing">Schedule Viewing</MenuItem>
                <MenuItem value="offer">Make Offer</MenuItem>
                <MenuItem value="follow_up">Follow Up</MenuItem>
              </Select>
            </FormControl>

            {/* Subject */}
            <TextField
              fullWidth
              label="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              margin="normal"
              required
              disabled={loading}
            />

            {/* Message */}
            <TextField
              fullWidth
              label="Message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              margin="normal"
              multiline
              rows={6}
              required
              disabled={loading}
              placeholder="Enter your message here..."
            />

            {/* Contact Info Note */}
            <Alert severity="info" sx={{ mt: 2 }}>
              Your contact information will be shared with the agent so they can respond to your inquiry.
            </Alert>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        {canContact() && (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading || !subject.trim() || !message.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            {loading ? 'Sending...' : 'Send Message'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ContactAgentDialog;
