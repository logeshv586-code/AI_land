from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
import random
from app.models import User, UserRole
from app.core.config import settings

class AgentAssignmentService:
    """Service for managing agent assignments to buyers and sellers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_buyer_agents(self, location_area: Optional[str] = None) -> List[User]:
        """Get available buyer agents, optionally filtered by service area"""
        query = self.db.query(User).filter(
            and_(
                User.user_role == UserRole.BUYER_AGENT,
                User.is_active == True,
                User.subscription_status == "active"
            )
        )
        
        # If location_area is provided, filter by service areas
        if location_area:
            query = query.filter(
                or_(
                    User.service_areas.is_(None),  # No restriction on service areas
                    User.service_areas.contains([location_area])  # Contains the specific area
                )
            )
        
        return query.all()
    
    def get_available_seller_agents(self, location_area: Optional[str] = None) -> List[User]:
        """Get available seller agents, optionally filtered by service area"""
        query = self.db.query(User).filter(
            and_(
                User.user_role == UserRole.SELLER_AGENT,
                User.is_active == True,
                User.subscription_status == "active"
            )
        )
        
        # If location_area is provided, filter by service areas
        if location_area:
            query = query.filter(
                or_(
                    User.service_areas.is_(None),  # No restriction on service areas
                    User.service_areas.contains([location_area])  # Contains the specific area
                )
            )
        
        return query.all()
    
    def assign_buyer_agent(self, buyer_id: int, agent_id: Optional[int] = None, location_area: Optional[str] = None) -> Optional[User]:
        """Assign a buyer agent to a buyer"""
        buyer = self.db.query(User).filter(
            and_(
                User.id == buyer_id,
                User.user_role == UserRole.BUYER
            )
        ).first()
        
        if not buyer:
            return None
        
        # If agent_id is provided, use that specific agent
        if agent_id:
            agent = self.db.query(User).filter(
                and_(
                    User.id == agent_id,
                    User.user_role == UserRole.BUYER_AGENT,
                    User.is_active == True
                )
            ).first()
            
            if agent:
                buyer.assigned_buyer_agent_id = agent.id
                self.db.commit()
                self.db.refresh(buyer)
                return agent
        
        # Auto-assign based on availability and load balancing
        available_agents = self.get_available_buyer_agents(location_area)
        
        if not available_agents:
            return None
        
        # Simple load balancing: assign to agent with fewest clients
        agent_with_min_clients = min(
            available_agents,
            key=lambda agent: len(agent.buyer_clients) if agent.buyer_clients else 0
        )
        
        buyer.assigned_buyer_agent_id = agent_with_min_clients.id
        self.db.commit()
        self.db.refresh(buyer)
        return agent_with_min_clients
    
    def assign_seller_agent(self, seller_id: int, agent_id: Optional[int] = None, location_area: Optional[str] = None) -> Optional[User]:
        """Assign a seller agent to a seller"""
        seller = self.db.query(User).filter(
            and_(
                User.id == seller_id,
                User.user_role == UserRole.SELLER
            )
        ).first()
        
        if not seller:
            return None
        
        # If agent_id is provided, use that specific agent
        if agent_id:
            agent = self.db.query(User).filter(
                and_(
                    User.id == agent_id,
                    User.user_role == UserRole.SELLER_AGENT,
                    User.is_active == True
                )
            ).first()
            
            if agent:
                seller.assigned_seller_agent_id = agent.id
                self.db.commit()
                self.db.refresh(seller)
                return agent
        
        # Auto-assign based on availability and load balancing
        available_agents = self.get_available_seller_agents(location_area)
        
        if not available_agents:
            return None
        
        # Simple load balancing: assign to agent with fewest clients
        agent_with_min_clients = min(
            available_agents,
            key=lambda agent: len(agent.seller_clients) if agent.seller_clients else 0
        )
        
        seller.assigned_seller_agent_id = agent_with_min_clients.id
        self.db.commit()
        self.db.refresh(seller)
        return agent_with_min_clients
    
    def unassign_buyer_agent(self, buyer_id: int) -> bool:
        """Remove buyer agent assignment"""
        buyer = self.db.query(User).filter(
            and_(
                User.id == buyer_id,
                User.user_role == UserRole.BUYER
            )
        ).first()
        
        if buyer:
            buyer.assigned_buyer_agent_id = None
            self.db.commit()
            return True
        return False
    
    def unassign_seller_agent(self, seller_id: int) -> bool:
        """Remove seller agent assignment"""
        seller = self.db.query(User).filter(
            and_(
                User.id == seller_id,
                User.user_role == UserRole.SELLER
            )
        ).first()
        
        if seller:
            seller.assigned_seller_agent_id = None
            self.db.commit()
            return True
        return False
    
    def get_client_list(self, agent_id: int) -> List[User]:
        """Get list of clients for an agent"""
        agent = self.db.query(User).filter(User.id == agent_id).first()
        
        if not agent:
            return []
        
        if agent.user_role == UserRole.BUYER_AGENT:
            return self.db.query(User).filter(
                and_(
                    User.assigned_buyer_agent_id == agent_id,
                    User.user_role == UserRole.BUYER
                )
            ).all()
        elif agent.user_role == UserRole.SELLER_AGENT:
            return self.db.query(User).filter(
                and_(
                    User.assigned_seller_agent_id == agent_id,
                    User.user_role == UserRole.SELLER
                )
            ).all()
        
        return []
    
    def can_communicate(self, sender_id: int, recipient_id: int) -> bool:
        """Check if two users can communicate directly based on their roles and agent assignments"""
        sender = self.db.query(User).filter(User.id == sender_id).first()
        recipient = self.db.query(User).filter(User.id == recipient_id).first()
        
        if not sender or not recipient:
            return False
        
        # Agents can always communicate
        if sender.user_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
            return True
        
        if recipient.user_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
            return True
        
        # Buyers can only communicate with their assigned buyer agent and seller agents
        if sender.user_role == UserRole.BUYER:
            if recipient.user_role == UserRole.SELLER_AGENT:
                return True
            if recipient.user_role == UserRole.BUYER_AGENT and sender.assigned_buyer_agent_id == recipient.id:
                return True
            return False
        
        # Sellers can only communicate with their assigned seller agent and buyer agents (through their seller agent)
        if sender.user_role == UserRole.SELLER:
            if recipient.user_role == UserRole.SELLER_AGENT and sender.assigned_seller_agent_id == recipient.id:
                return True
            # Sellers cannot directly communicate with buyer agents - must go through their seller agent
            return False
        
        return False
    
    def get_communication_path(self, sender_id: int, target_recipient_id: int) -> List[int]:
        """Get the communication path between two users, routing through agents if necessary"""
        sender = self.db.query(User).filter(User.id == sender_id).first()
        target = self.db.query(User).filter(User.id == target_recipient_id).first()
        
        if not sender or not target:
            return []
        
        # Direct communication allowed
        if self.can_communicate(sender_id, target_recipient_id):
            return [sender_id, target_recipient_id]
        
        # Route through agents
        if sender.user_role == UserRole.BUYER and target.user_role == UserRole.SELLER:
            # Buyer wants to contact seller: Buyer -> Buyer Agent -> Seller Agent -> Seller
            path = [sender_id]
            
            if sender.assigned_buyer_agent_id:
                path.append(sender.assigned_buyer_agent_id)
            
            if target.assigned_seller_agent_id:
                path.append(target.assigned_seller_agent_id)
            
            path.append(target_recipient_id)
            return path
        
        if sender.user_role == UserRole.SELLER and target.user_role == UserRole.BUYER:
            # Seller wants to contact buyer: Seller -> Seller Agent -> Buyer Agent -> Buyer
            path = [sender_id]
            
            if sender.assigned_seller_agent_id:
                path.append(sender.assigned_seller_agent_id)
            
            if target.assigned_buyer_agent_id:
                path.append(target.assigned_buyer_agent_id)
            
            path.append(target_recipient_id)
            return path
        
        return [sender_id, target_recipient_id]
    
    def auto_assign_agents_on_registration(self, user_id: int, location_area: Optional[str] = None) -> bool:
        """Automatically assign agents to new buyers and sellers upon registration"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        if user.user_role == UserRole.BUYER:
            agent = self.assign_buyer_agent(user_id, location_area=location_area)
            return agent is not None
        elif user.user_role == UserRole.SELLER:
            agent = self.assign_seller_agent(user_id, location_area=location_area)
            return agent is not None
        
        return True  # Agents don't need assignment