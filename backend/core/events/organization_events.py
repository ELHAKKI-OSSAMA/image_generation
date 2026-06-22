from typing import Dict, Any, Callable, Set, Coroutine
from uuid import UUID
from collections import defaultdict
from fastapi import Depends

from core.cache import CacheService
from .event_types import EventType

EventHandler = Callable[[EventType, UUID, Dict[str, Any]], Coroutine[Any, Any, None]]

class OrganizationEvents:
    """Event system for real-time organization updates."""
    
    def __init__(self, cache_service: CacheService = Depends()):
        """Initialize event system with cache service."""
        self.cache = cache_service
        self.subscribers: Dict[UUID, Set[EventHandler]] = defaultdict(set)
        self.global_subscribers: Set[EventHandler] = set()

    async def publish(
        self,
        event_type: EventType,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Publish an organization event."""
        # Invalidate cache
        await self.cache.invalidate_organization(org_id)
        
        # Notify organization-specific subscribers
        if org_subscribers := self.subscribers.get(org_id):
            for subscriber in org_subscribers:
                await subscriber(event_type, org_id, data)
        
        # Notify global subscribers
        for subscriber in self.global_subscribers:
            await subscriber(event_type, org_id, data)

    def subscribe(
        self,
        handler: EventHandler,
        org_id: UUID = None
    ) -> Callable[[], None]:
        """Subscribe to organization events.
        
        If org_id is provided, only receive events for that organization.
        If org_id is None, receive events for all organizations.
        
        Returns an unsubscribe function.
        """
        if org_id:
            self.subscribers[org_id].add(handler)
            
            def unsubscribe():
                self.subscribers[org_id].discard(handler)
                if not self.subscribers[org_id]:
                    del self.subscribers[org_id]
        else:
            self.global_subscribers.add(handler)
            
            def unsubscribe():
                self.global_subscribers.discard(handler)
                
        return unsubscribe

    async def notify_org_created(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when a new organization is created."""
        await self.publish(EventType.ORG_CREATED, org_id, data)

    async def notify_org_updated(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when an organization is updated."""
        await self.publish(EventType.ORG_UPDATED, org_id, data)

    async def notify_org_deleted(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when an organization is deleted."""
        await self.publish(EventType.ORG_DELETED, org_id, data)

    async def notify_member_added(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when a member is added to an organization."""
        await self.publish(EventType.MEMBER_ADDED, org_id, data)

    async def notify_member_removed(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when a member is removed from an organization."""
        await self.publish(EventType.MEMBER_REMOVED, org_id, data)

    async def notify_member_updated(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when a member's details are updated."""
        await self.publish(EventType.MEMBER_UPDATED, org_id, data)

    async def notify_role_updated(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when a member's role is updated."""
        await self.publish(EventType.ROLE_UPDATED, org_id, data)

    async def notify_permission_updated(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when permissions are updated."""
        await self.publish(EventType.PERMISSION_UPDATED, org_id, data)

    async def notify_status_updated(
        self,
        org_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Notify when organization status is updated."""
        await self.publish(EventType.STATUS_UPDATED, org_id, data)
