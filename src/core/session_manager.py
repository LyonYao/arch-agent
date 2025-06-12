#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
会话管理模块
管理用户与架构设计Agent的交互会话
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Session:
    """用户会话类，存储单个会话的信息"""
    
    def __init__(self, session_id: str = None):
        """
        初始化会话
        
        Args:
            session_id: 会话ID，如果为None则自动生成
        """
        self.session_id = session_id or f"session_{int(time.time())}"
        self.created_at = time.time()
        self.updated_at = time.time()
        self.interactions = []  # 存储用户交互历史
        self.current_architecture = None  # 当前架构设计
        self.name = f"未命名会话 {self.session_id[-8:]}"
    
    def add_interaction(self, user_input: str, ai_response: Dict[str, Any]) -> None:
        """
        添加一次交互记录
        
        Args:
            user_input: 用户输入
            ai_response: AI响应
        """
        interaction = {
            "timestamp": time.time(),
            "user_input": user_input,
            "ai_response": ai_response
        }
        self.interactions.append(interaction)
        self.updated_at = time.time()
        self.current_architecture = ai_response
    
    def get_context_for_next_interaction(self) -> str:
        """
        获取下一次交互的上下文信息
        
        Returns:
            str: 上下文信息
        """
        context = []
        
        # 添加历史交互记录
        for i, interaction in enumerate(self.interactions):
            context.append(f"交互 {i+1}:")
            context.append(f"用户: {interaction['user_input']}")
            # 不添加完整的AI响应，只添加概述
            if "architecture_overview" in interaction["ai_response"]:
                context.append(f"AI响应概述: {interaction['ai_response']['architecture_overview'][:200]}...")
            context.append("")
        
        return "\n".join(context)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将会话转换为字典
        
        Returns:
            Dict: 会话字典
        """
        return {
            "session_id": self.session_id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "interactions": self.interactions,
            "current_architecture": self.current_architecture
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """
        从字典创建会话
        
        Args:
            data: 会话字典
            
        Returns:
            Session: 会话对象
        """
        session = cls(session_id=data.get("session_id"))
        session.name = data.get("name", session.name)
        session.created_at = data.get("created_at", session.created_at)
        session.updated_at = data.get("updated_at", session.updated_at)
        session.interactions = data.get("interactions", [])
        session.current_architecture = data.get("current_architecture")
        return session


class SessionManager:
    """会话管理器，管理所有用户会话"""
    
    def __init__(self, sessions_dir: str = None):
        """
        初始化会话管理器
        
        Args:
            sessions_dir: 会话存储目录，如果为None则使用默认目录
        """
        # 设置会话存储目录
        if sessions_dir is None:
            # 默认存储在用户目录下
            home_dir = os.path.expanduser("~")
            self.sessions_dir = os.path.join(home_dir, ".architect_agent", "sessions")
        else:
            self.sessions_dir = sessions_dir
        
        # 确保目录存在
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # 当前活动会话
        self.active_session = None
        
        # 加载所有会话
        self.sessions = {}
        self._load_sessions()
    
    def _load_sessions(self) -> None:
        """加载所有会话"""
        try:
            # 遍历会话目录
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                            session = Session.from_dict(session_data)
                            self.sessions[session.session_id] = session
                            logger.info(f"加载会话: {session.name} ({session.session_id})")
                    except Exception as e:
                        logger.error(f"加载会话文件 {file_path} 失败: {str(e)}")
            
            logger.info(f"共加载 {len(self.sessions)} 个会话")
        except Exception as e:
            logger.error(f"加载会话失败: {str(e)}")
    
    def create_session(self) -> Session:
        """
        创建新会话
        
        Returns:
            Session: 新创建的会话
        """
        session = Session()
        self.sessions[session.session_id] = session
        self.active_session = session
        self._save_session(session)
        logger.info(f"创建新会话: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Session]: 会话对象，如果不存在则返回None
        """
        return self.sessions.get(session_id)
    
    def set_active_session(self, session_id: str) -> bool:
        """
        设置活动会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功设置
        """
        if session_id in self.sessions:
            self.active_session = self.sessions[session_id]
            logger.info(f"设置活动会话: {session_id}")
            return True
        return False
    
    def get_active_session(self) -> Optional[Session]:
        """
        获取当前活动会话
        
        Returns:
            Optional[Session]: 活动会话对象，如果不存在则返回None
        """
        return self.active_session
    
    def add_interaction(self, user_input: str, ai_response: Dict[str, Any]) -> None:
        """
        添加交互记录到当前活动会话
        
        Args:
            user_input: 用户输入
            ai_response: AI响应
        """
        if self.active_session:
            self.active_session.add_interaction(user_input, ai_response)
            self._save_session(self.active_session)
            logger.info(f"添加交互记录到会话: {self.active_session.session_id}")
        else:
            logger.warning("没有活动会话，无法添加交互记录")
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """
        重命名会话
        
        Args:
            session_id: 会话ID
            new_name: 新名称
            
        Returns:
            bool: 是否成功重命名
        """
        if session_id in self.sessions:
            self.sessions[session_id].name = new_name
            self._save_session(self.sessions[session_id])
            logger.info(f"重命名会话 {session_id} 为: {new_name}")
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功删除
        """
        if session_id in self.sessions:
            # 删除会话文件
            file_path = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 从会话字典中删除
            session = self.sessions.pop(session_id)
            
            # 如果删除的是当前活动会话，则清空活动会话
            if self.active_session and self.active_session.session_id == session_id:
                self.active_session = None
            
            logger.info(f"删除会话: {session_id}")
            return True
        return False
        
    def delete_all_sessions(self) -> int:
        """
        删除所有会话
        
        Returns:
            int: 删除的会话数量
        """
        session_ids = list(self.sessions.keys())
        count = 0
        
        for session_id in session_ids:
            if self.delete_session(session_id):
                count += 1
        
        # 清空活动会话
        self.active_session = None
        
        logger.info(f"删除了所有 {count} 个会话")
        return count
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话的摘要信息
        
        Returns:
            List[Dict]: 会话摘要列表
        """
        return [
            {
                "session_id": session.session_id,
                "name": session.name,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "interaction_count": len(session.interactions)
            }
            for session in sorted(
                self.sessions.values(),
                key=lambda s: s.updated_at,
                reverse=True
            )
        ]
    
    def _save_session(self, session: Session) -> None:
        """
        保存会话到文件
        
        Args:
            session: 会话对象
        """
        try:
            file_path = os.path.join(self.sessions_dir, f"{session.session_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"保存会话: {session.session_id}")
        except Exception as e:
            logger.error(f"保存会话 {session.session_id} 失败: {str(e)}")