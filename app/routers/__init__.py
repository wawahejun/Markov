# 路由模块初始化文件
from .users import router as users_router
from .recommendations import router as recommendations_router
from .analytics import router as analytics_router

__all__ = ["users_router", "recommendations_router", "analytics_router"]