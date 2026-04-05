#!/usr/bin/env python3
# 自动回复引擎

import json
import re
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchConfidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

@dataclass
class MatchResult:
    """匹配结果"""
    category: str
    confidence: float
    matched_keywords: List[str]
    extracted_location: Optional[str] = None
    is_emergency: bool = False
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}

class AutoReplyEngine:
    """自动回复引擎"""
    
    def __init__(self, keywords_path: str, templates_path: str):
        """初始化引擎"""
        self.keywords_path = keywords_path
        self.templates_path = templates_path
        self.keywords_data = self._load_keywords()
        self.templates_data = self._load_templates()
        self._build_keyword_index()
        
    def _load_keywords(self) -> Dict:
        """加载关键词配置"""
        try:
            with open(self.keywords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载关键词配置失败: {e}")
            return {}
    
    def _load_templates(self) -> Dict:
        """加载模板配置"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载模板配置失败: {e}")
            return {}
    
    def _build_keyword_index(self):
        """构建关键词索引"""
        self.keyword_to_category = {}
        self.category_keywords = {}
        
        if not self.keywords_data:
            return
        
        for category in self.keywords_data.get('categories', []):
            cat_id = category['id']
            self.category_keywords[cat_id] = {
                'keywords': set(category.get('keywords', [])),
                'location_keywords': set(category.get('location_keywords', [])),
                'confidence_threshold': category.get('confidence_threshold', 0.5)
            }
            
            # 建立关键词到类别的映射
            for keyword in category.get('keywords', []):
                if keyword not in self.keyword_to_category:
                    self.keyword_to_category[keyword] = []
                self.keyword_to_category[keyword].append(cat_id)
    
    def analyze_message(self, message: str) -> MatchResult:
        """分析消息内容"""
        message_lower = message.lower()
        
        # 检查紧急关键词
        is_emergency = self._check_emergency(message_lower)
        
        # 提取位置信息
        location = self._extract_location(message)
        
        # 匹配类别
        category_matches = self._match_category(message_lower)
        
        if not category_matches:
            # 没有匹配到任何类别
            return MatchResult(
                category=self.keywords_data.get('matching_rules', {}).get('fallback_category', 'unknown'),
                confidence=0.0,
                matched_keywords=[],
                extracted_location=location,
                is_emergency=is_emergency
            )
        
        # 选择最佳匹配
        best_match = max(category_matches, key=lambda x: x['confidence'])
        
        return MatchResult(
            category=best_match['category'],
            confidence=best_match['confidence'],
            matched_keywords=best_match['matched_keywords'],
            extracted_location=location,
            is_emergency=is_emergency,
            variables=self._extract_variables(message, best_match['category'])
        )
    
    def _check_emergency(self, message: str) -> bool:
        """检查是否包含紧急关键词"""
        emergency_keywords = self.keywords_data.get('emergency_keywords', [])
        for keyword in emergency_keywords:
            if keyword.lower() in message:
                return True
        return False
    
    def _extract_location(self, message: str) -> Optional[str]:
        """提取位置信息"""
        location_patterns = self.keywords_data.get('location_patterns', {})
        
        for location_name, patterns in location_patterns.items():
            for pattern in patterns:
                if pattern.lower() in message.lower():
                    return location_name
        
        return None
    
    def _match_category(self, message: str) -> List[Dict]:
        """匹配消息到类别"""
        matches = []
        
        for category_id, category_info in self.category_keywords.items():
            matched_keywords = []
            confidence = 0.0
            
            # 检查关键词匹配
            for keyword in category_info['keywords']:
                if self._match_keyword(keyword, message):
                    matched_keywords.append(keyword)
                    confidence += 1.0  # 完全匹配
            
            # 检查同义词匹配
            synonyms = self.keywords_data.get('synonyms', {})
            for keyword, synonym_list in synonyms.items():
                if keyword in category_info['keywords']:
                    for synonym in synonym_list:
                        if self._match_keyword(synonym, message):
                            matched_keywords.append(f"{keyword}(同义词:{synonym})")
                            confidence += 0.8  # 同义词匹配
            
            if matched_keywords:
                # 计算最终置信度
                base_confidence = confidence / max(len(category_info['keywords']), 1)
                
                # 应用匹配规则
                rules = self.keywords_data.get('matching_rules', {})
                if base_confidence >= rules.get('minimum_confidence', 0.5):
                    matches.append({
                        'category': category_id,
                        'confidence': min(base_confidence, 1.0),
                        'matched_keywords': matched_keywords,
                        'threshold': category_info['confidence_threshold']
                    })
        
        return matches
    
    def _match_keyword(self, keyword: str, message: str) -> bool:
        """匹配关键词"""
        # 简单包含匹配
        if keyword.lower() in message:
            return True
        
        # 中文分词简单处理（按字符匹配）
        if len(keyword) > 1:
            # 检查是否所有字符都在消息中（顺序可能不同）
            keyword_chars = set(keyword)
            message_chars = set(message)
            if keyword_chars.issubset(message_chars):
                # 进一步检查顺序
                pattern = '.*'.join(re.escape(char) for char in keyword)
                if re.search(pattern, message):
                    return True
        
        return False
    
    def _extract_variables(self, message: str, category: str) -> Dict[str, Any]:
        """提取模板变量"""
        variables = {}
        
        # 提取位置
        location = self._extract_location(message)
        if location:
            variables['location'] = location
        
        # 根据类别设置默认变量
        if category == 'rvm_full':
            variables['estimated_time'] = '2天内完成'
            variables['responsible_party'] = 'KDEBS'
            variables['contact_number'] = '+60 11-1072 8228'
        elif category == 'technical_issue':
            variables['estimated_time'] = '24小时内'
            variables['emergency_contact'] = '+60 11-1095 8228'
        elif category == 'complaint':
            variables['response_time'] = '24小时内'
            variables['emergency_contact'] = '+60 11-1095 8228'
        
        return variables
    
    def get_reply_template(self, category: str, is_emergency: bool = False) -> Optional[Dict]:
        """获取回复模板"""
        templates = self.templates_data.get('templates', [])
        
        # 如果是紧急情况，优先使用紧急模板
        if is_emergency:
            emergency_templates = self.templates_data.get('emergency_templates', [])
            if emergency_templates:
                return emergency_templates[0]  # 使用第一个紧急模板
        
        # 查找对应类别的模板
        for template in templates:
            if template['category'] == category:
                return template
        
        # 如果没有找到，使用未知问题模板
        for template in templates:
            if template['category'] == 'unknown':
                return template
        
        return None
    
    def generate_reply(self, template: Dict, variables: Dict[str, Any]) -> str:
        """生成回复内容"""
        content = template['content']
        
        # 替换变量
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(var_value))
        
        # 处理未替换的变量
        for var_info in template.get('variables', {}).values():
            var_name = var_info.get('name', '')
            placeholder = f"{{{var_name}}}"
            if placeholder in content:
                default_value = var_info.get('default', '')
                content = content.replace(placeholder, str(default_value))
        
        return content
    
    def process_message(self, message: str, customer_info: Optional[Dict] = None) -> Dict[str, Any]:
        """处理消息并生成回复"""
        start_time = datetime.now()
        
        try:
            # 分析消息
            match_result = self.analyze_message(message)
            
            # 获取模板
            template = self.get_reply_template(
                match_result.category, 
                match_result.is_emergency
            )
            
            if not template:
                logger.warning(f"未找到类别 {match_result.category} 的模板")
                return {
                    'success': False,
                    'error': 'Template not found',
                    'match_result': match_result.__dict__
                }
            
            # 合并变量
            variables = match_result.variables.copy()
            if customer_info:
                variables.update(customer_info)
            
            # 生成回复
            reply_content = self.generate_reply(template, variables)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'reply': reply_content,
                'template_id': template.get('id', 'unknown'),
                'category': match_result.category,
                'confidence': match_result.confidence,
                'is_emergency': match_result.is_emergency,
                'extracted_location': match_result.extracted_location,
                'matched_keywords': match_result.matched_keywords,
                'processing_time_seconds': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"消息处理完成: category={match_result.category}, confidence={match_result.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# 使用示例
def main():
    """使用示例"""
    # 初始化引擎
    engine = AutoReplyEngine(
        keywords_path='config/keywords.json',
        templates_path='config/templates.json'
    )
    
    # 测试消息
    test_messages = [
        "Dataran Banting RVM已满，请清理",
        "RVM进度怎么样了？",
        "机器坏了，不能用",
        "怎么使用RVM？",
        "我要投诉，服务太慢了",
        "谢谢你们的服务，很好",
        "我想了解合作机会",
        "你好",
        "再见",
        "紧急！RVM着火了！"
    ]
    
    print("=" * 60)
    print("自动回复引擎测试")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. 测试消息: {message}")
        print("-" * 40)
        
        result = engine.process_message(message)
        
        if result['success']:
            print(f"   类别: {result['category']}")
            print(f"   置信度: {result['confidence']:.2f}")
            print(f"   紧急: {'是' if result['is_emergency'] else '否'}")
            print(f"   位置: {result['extracted_location'] or '未识别'}")
            print(f"   匹配关键词: {', '.join(result['matched_keywords'])}")
            print(f"   处理时间: {result['processing_time_seconds']:.3f}秒")
            print(f"\n   回复内容:\n   {result['reply']}")
        else:
            print(f"   处理失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()