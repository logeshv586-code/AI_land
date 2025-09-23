"""
Communication Validator Service
Enforces agent-mediated communication rules in the real estate platform
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from sqlalchemy.orm import Session
from app.models import User, UserRole, Message, PropertyListing

class CommunicationRule(Enum):
    """Communication rules for different user types"""
    BUYER_TO_SELLER_AGENT = "buyer_to_seller_agent"
    SELLER_TO_BUYER_AGENT = "seller_to_buyer_agent"
    AGENT_TO_AGENT = "agent_to_agent"
    AGENT_TO_CLIENT = "agent_to_client"
    DIRECT_FORBIDDEN = "direct_forbidden"

class CommunicationValidator:
    """Validates and enforces communication rules"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, Dict[str, CommunicationRule]]:
        """Initialize communication rules matrix"""
        return {
            UserRole.BUYER.value: {
                UserRole.SELLER.value: CommunicationRule.DIRECT_FORBIDDEN,
                UserRole.BUYER_AGENT.value: CommunicationRule.AGENT_TO_CLIENT,
                UserRole.SELLER_AGENT.value: CommunicationRule.BUYER_TO_SELLER_AGENT,
            },
            UserRole.SELLER.value: {
                UserRole.BUYER.value: CommunicationRule.DIRECT_FORBIDDEN,
                UserRole.SELLER_AGENT.value: CommunicationRule.AGENT_TO_CLIENT,
                UserRole.BUYER_AGENT.value: CommunicationRule.SELLER_TO_BUYER_AGENT,
            },
            UserRole.BUYER_AGENT.value: {
                UserRole.BUYER.value: CommunicationRule.AGENT_TO_CLIENT,
                UserRole.SELLER.value: CommunicationRule.SELLER_TO_BUYER_AGENT,
                UserRole.SELLER_AGENT.value: CommunicationRule.AGENT_TO_AGENT,
            },
            UserRole.SELLER_AGENT.value: {
                UserRole.SELLER.value: CommunicationRule.AGENT_TO_CLIENT,
                UserRole.BUYER.value: CommunicationRule.BUYER_TO_SELLER_AGENT,
                UserRole.BUYER_AGENT.value: CommunicationRule.AGENT_TO_AGENT,
            }
        }
    
    def validate_communication(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate if communication is allowed between sender and recipient
        
        Returns:
            Tuple[bool, str, Optional[Dict]]: (is_allowed, message, suggestions)
        """
        sender_role = sender.user_role.value if hasattr(sender.user_role, 'value') else sender.user_role
        recipient_role = recipient.user_role.value if hasattr(recipient.user_role, 'value') else recipient.user_role
        
        # Check if communication rule exists
        if sender_role not in self.rules:
            return False, f"Unknown sender role: {sender_role}", None
        
        if recipient_role not in self.rules[sender_role]:
            return False, f"Communication not defined between {sender_role} and {recipient_role}", None
        
        rule = self.rules[sender_role][recipient_role]
        
        # Apply rule validation
        if rule == CommunicationRule.DIRECT_FORBIDDEN:
            return self._handle_forbidden_communication(sender, recipient, context)
        elif rule == CommunicationRule.BUYER_TO_SELLER_AGENT:
            return self._validate_buyer_to_seller_agent(sender, recipient, context)
        elif rule == CommunicationRule.SELLER_TO_BUYER_AGENT:
            return self._validate_seller_to_buyer_agent(sender, recipient, context)
        elif rule == CommunicationRule.AGENT_TO_AGENT:
            return self._validate_agent_to_agent(sender, recipient, context)
        elif rule == CommunicationRule.AGENT_TO_CLIENT:
            return self._validate_agent_to_client(sender, recipient, context)
        
        return True, "Communication allowed", None
    
    def _handle_forbidden_communication(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict]
    ) -> Tuple[bool, str, Dict]:
        """Handle forbidden direct communication"""
        sender_role = sender.user_role.value if hasattr(sender.user_role, 'value') else sender.user_role
        recipient_role = recipient.user_role.value if hasattr(recipient.user_role, 'value') else recipient.user_role
        
        suggestions = {}
        
        if sender_role == UserRole.BUYER.value and recipient_role == UserRole.SELLER.value:
            message = "Direct communication between buyers and sellers is not allowed. Please work through your respective agents."
            suggestions = {
                "buyer_action": "Contact a buyer agent to represent you in this transaction",
                "seller_action": "Work with a seller agent to handle buyer communications",
                "recommended_flow": "Buyer → Buyer Agent → Seller Agent → Seller"
            }
        elif sender_role == UserRole.SELLER.value and recipient_role == UserRole.BUYER.value:
            message = "Direct communication between sellers and buyers is not allowed. Please work through your respective agents."
            suggestions = {
                "seller_action": "Contact a seller agent to represent you in this transaction",
                "buyer_action": "Work with a buyer agent to handle seller communications",
                "recommended_flow": "Seller → Seller Agent → Buyer Agent → Buyer"
            }
        else:
            message = f"Direct communication between {sender_role} and {recipient_role} is not allowed."
            suggestions = {"action": "Please work through appropriate agents"}
        
        return False, message, suggestions
    
    def _validate_buyer_to_seller_agent(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict]
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Validate buyer to seller agent communication"""
        # Buyers can contact seller agents directly about properties
        if context and context.get("property_id"):
            return True, "Buyer can contact seller agent about property", {
                "communication_type": "property_inquiry",
                "guidelines": [
                    "Keep communication professional and property-focused",
                    "Consider working with a buyer agent for negotiations",
                    "All offers should go through a buyer agent"
                ]
            }
        
        return True, "Buyer to seller agent communication allowed", {
            "recommendation": "Consider working with a buyer agent for better representation"
        }
    
    def _validate_seller_to_buyer_agent(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict]
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Validate seller to buyer agent communication"""
        # Sellers should work through seller agents, but can communicate with buyer agents
        return True, "Seller to buyer agent communication allowed", {
            "recommendation": "Consider working with a seller agent for better representation",
            "guidelines": [
                "Professional communication only",
                "Property-related inquiries are acceptable",
                "Negotiations should involve a seller agent"
            ]
        }
    
    def _validate_agent_to_agent(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict]
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Validate agent to agent communication"""
        return True, "Agent to agent communication fully allowed", {
            "communication_type": "professional",
            "capabilities": [
                "Property negotiations",
                "Client coordination",
                "Transaction management",
                "Market information sharing"
            ]
        }
    
    def _validate_agent_to_client(
        self, 
        sender: User, 
        recipient: User, 
        context: Optional[Dict]
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Validate agent to client communication"""
        return True, "Agent to client communication fully allowed", {
            "communication_type": "client_service",
            "responsibilities": [
                "Property recommendations",
                "Market updates",
                "Transaction guidance",
                "Professional representation"
            ]
        }
    
    def get_communication_guidelines(self, user_role: str) -> Dict[str, List[str]]:
        """Get communication guidelines for a specific user role"""
        guidelines = {
            UserRole.BUYER.value: [
                "You can browse properties and contact seller agents directly",
                "For negotiations and offers, work with a buyer agent",
                "Direct communication with sellers is not allowed",
                "Consider hiring a buyer agent for professional representation"
            ],
            UserRole.SELLER.value: [
                "You can list properties and track performance",
                "Work with a seller agent to communicate with buyer agents",
                "Direct communication with buyers is not allowed",
                "Seller agents handle negotiations and offers on your behalf"
            ],
            UserRole.BUYER_AGENT.value: [
                "You represent buyers in property transactions",
                "You can communicate with seller agents and sellers",
                "Help buyers find properties and negotiate deals",
                "Provide professional guidance throughout the buying process"
            ],
            UserRole.SELLER_AGENT.value: [
                "You represent sellers in property transactions",
                "You can communicate with buyer agents and buyers",
                "Help sellers market properties and negotiate deals",
                "Provide professional guidance throughout the selling process"
            ]
        }
        
        return {
            "role": user_role,
            "guidelines": guidelines.get(user_role, []),
            "communication_matrix": self._get_communication_matrix_for_role(user_role)
        }
    
    def _get_communication_matrix_for_role(self, user_role: str) -> Dict[str, str]:
        """Get communication matrix for a specific role"""
        if user_role not in self.rules:
            return {}
        
        matrix = {}
        for target_role, rule in self.rules[user_role].items():
            if rule == CommunicationRule.DIRECT_FORBIDDEN:
                matrix[target_role] = "❌ Not Allowed - Use agents"
            elif rule == CommunicationRule.BUYER_TO_SELLER_AGENT:
                matrix[target_role] = "✅ Allowed - Property inquiries"
            elif rule == CommunicationRule.SELLER_TO_BUYER_AGENT:
                matrix[target_role] = "✅ Allowed - Consider seller agent"
            elif rule == CommunicationRule.AGENT_TO_AGENT:
                matrix[target_role] = "✅ Fully Allowed - Professional"
            elif rule == CommunicationRule.AGENT_TO_CLIENT:
                matrix[target_role] = "✅ Fully Allowed - Client service"
        
        return matrix
    
    def suggest_communication_path(
        self, 
        sender: User, 
        target_recipient: User, 
        db: Session
    ) -> Dict[str, any]:
        """Suggest the best communication path between users"""
        sender_role = sender.user_role.value if hasattr(sender.user_role, 'value') else sender.user_role
        target_role = target_recipient.user_role.value if hasattr(target_recipient.user_role, 'value') else target_recipient.user_role
        
        # Check if direct communication is allowed
        is_allowed, message, suggestions = self.validate_communication(sender, target_recipient)
        
        if is_allowed:
            return {
                "direct_communication": True,
                "path": [sender.username, target_recipient.username],
                "message": message,
                "suggestions": suggestions
            }
        
        # Find alternative communication path
        alternative_path = self._find_alternative_path(sender_role, target_role, db)
        
        return {
            "direct_communication": False,
            "message": message,
            "alternative_path": alternative_path,
            "suggestions": suggestions
        }
    
    def _find_alternative_path(
        self, 
        sender_role: str, 
        target_role: str, 
        db: Session
    ) -> Dict[str, any]:
        """Find alternative communication path through agents"""
        if sender_role == UserRole.BUYER.value and target_role == UserRole.SELLER.value:
            # Buyer → Buyer Agent → Seller Agent → Seller
            buyer_agents = db.query(User).filter(User.user_role == UserRole.BUYER_AGENT).limit(5).all()
            seller_agents = db.query(User).filter(User.user_role == UserRole.SELLER_AGENT).limit(5).all()
            
            return {
                "recommended_path": "Buyer → Buyer Agent → Seller Agent → Seller",
                "step1": "Find a buyer agent to represent you",
                "step2": "Buyer agent contacts seller agent",
                "step3": "Seller agent communicates with seller",
                "available_buyer_agents": [{"id": agent.id, "name": f"{agent.first_name} {agent.last_name}"} for agent in buyer_agents],
                "available_seller_agents": [{"id": agent.id, "name": f"{agent.first_name} {agent.last_name}"} for agent in seller_agents]
            }
        elif sender_role == UserRole.SELLER.value and target_role == UserRole.BUYER.value:
            # Seller → Seller Agent → Buyer Agent → Buyer
            seller_agents = db.query(User).filter(User.user_role == UserRole.SELLER_AGENT).limit(5).all()
            buyer_agents = db.query(User).filter(User.user_role == UserRole.BUYER_AGENT).limit(5).all()
            
            return {
                "recommended_path": "Seller → Seller Agent → Buyer Agent → Buyer",
                "step1": "Find a seller agent to represent you",
                "step2": "Seller agent contacts buyer agent",
                "step3": "Buyer agent communicates with buyer",
                "available_seller_agents": [{"id": agent.id, "name": f"{agent.first_name} {agent.last_name}"} for agent in seller_agents],
                "available_buyer_agents": [{"id": agent.id, "name": f"{agent.first_name} {agent.last_name}"} for agent in buyer_agents]
            }
        
        return {
            "message": "No alternative path available",
            "recommendation": "Contact platform support for assistance"
        }

# Export singleton instance
communication_validator = CommunicationValidator()
