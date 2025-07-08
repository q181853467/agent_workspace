from typing import AsyncGenerator
import asyncio
import time
import uuid
from app.services.model_service import BaseModelService
from app.schemas.chat import (
    ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk,
    ChatCompletionChoice, ChatCompletionUsage, ChatMessage, MessageRole,
    ChatCompletionChunkChoice, ChatCompletionChunkDelta
)
from app.models.model import Model

class MockModelService(BaseModelService):
    """Mock model service for demonstration purposes"""
    
    def __init__(self):
        self.mock_responses = {
            "gpt-4": {
                "base": "我是GPT-4，OpenAI开发的最先进的大语言模型。我拥有强大的推理能力，可以处理复杂的多步骤问题。",
                "capabilities": ["编程", "数学", "写作", "分析", "创意", "翻译", "总结"],
                "response_time": (1.0, 3.0)  # 响应时间范围（秒）
            },
            "gpt-3.5-turbo": {
                "base": "我是GPT-3.5 Turbo，快速高效的AI助手。我在保持高质量输出的同时，能够快速响应各种询问。",
                "capabilities": ["对话", "问答", "文本处理", "简单编程", "总结"],
                "response_time": (0.5, 1.5)
            },
            "deepseek-coder": {
                "base": "我是DeepSeek Coder，专门为编程任务优化的AI模型。我在代码生成、调试和算法设计方面表现出色。",
                "capabilities": ["编程", "调试", "代码审查", "算法设计", "架构设计"],
                "response_time": (0.8, 2.0)
            },
            "deepseek-chat": {
                "base": "我是DeepSeek Chat，由深度求索开发的对话AI模型。我专注于中文对话，理解中国文化背景。",
                "capabilities": ["中文对话", "文学创作", "古诗词", "历史文化", "生活建议"],
                "response_time": (0.6, 1.8)
            },
            "claude-3": {
                "base": "我是Claude 3，Anthropic开发的AI助手。我致力于提供安全、有用、诚实的帮助，注重伦理和安全性。",
                "capabilities": ["分析", "写作", "总结", "推理", "道德判断", "创意"],
                "response_time": (1.2, 2.5)
            }
        }
        
        # 智能回复模板
        self.response_templates = {
            "greeting": [
                "您好！很高兴为您服务。我可以帮助您解决各种问题，请告诉我您需要什么帮助。",
                "欢迎使用我们的AI服务！我是您的智能助手，随时准备为您提供帮助。",
                "您好！我是您的AI助手，擅长处理各种任务。请问今天我能为您做些什么？"
            ],
            "programming": [
                "作为编程专家，我可以帮助您：\n1. 编写和优化代码\n2. 调试程序错误\n3. 设计算法和数据结构\n4. 代码审查和重构\n\n请描述您的具体需求。",
                "我很乐意帮助您解决编程问题！无论是语法错误、逻辑问题还是架构设计，我都能提供专业建议。",
                "编程是我的强项！我可以支持多种编程语言，包括Python、JavaScript、Java、C++等。请告诉我您遇到的具体问题。"
            ],
            "analysis": [
                "我可以为您提供深入的分析，包括：\n• 数据分析和可视化\n• 趋势预测\n• 问题根因分析\n• 方案对比评估\n\n请分享您需要分析的内容。",
                "分析和推理是我的核心能力。我可以帮助您从不同角度思考问题，提供客观的见解和建议。",
                "让我为您进行专业分析。我会运用逻辑推理和数据分析方法，为您提供有价值的洞察。"
            ],
            "creative": [
                "创意工作是我喜欢的挑战！我可以帮助您：\n✨ 创意写作和故事创作\n🎨 设计方案和概念开发\n💡 头脑风暴和创意激发\n📝 文案策划和内容创作",
                "我很兴奋能参与您的创意项目！无论是艺术创作、文学写作还是商业创意，我都能提供独特的视角。",
                "创意无限！我可以从多个维度为您的项目注入新的想法和灵感。让我们一起创造出色的作品。"
            ]
        }
    
    async def chat_completion(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> ChatCompletionResponse:
        """Generate mock completion response"""
        import random
        
        # Get model configuration
        model_config = self.mock_responses.get(model.name, {
            "base": f"我是{model.name}，很高兴为您服务！",
            "capabilities": ["通用对话"],
            "response_time": (0.5, 2.0)
        })
        
        # Simulate realistic processing time
        response_time = random.uniform(*model_config["response_time"])
        await asyncio.sleep(response_time)
        
        # Analyze user input
        last_message = request.messages[-1].content if request.messages else ""
        message_lower = last_message.lower()
        
        # Generate contextual response
        response_content = self._generate_contextual_response(
            last_message, model_config, model.name
        )
        
        # Add conversation context awareness
        if len(request.messages) > 1:
            response_content = self._add_context_awareness(request.messages, response_content)
        
        # Calculate realistic token usage
        prompt_tokens = sum(len(msg.content) // 4 for msg in request.messages)  # Approximate tokenization
        completion_tokens = len(response_content) // 4
        total_tokens = prompt_tokens + completion_tokens
        
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=model.name,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        content=response_content
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
        )
    
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate mock streaming response"""
        # Get the complete response first
        complete_response = await self.chat_completion(request, model)
        content = complete_response.choices[0].message.content
        
        # Split content into chunks for streaming
        words = content.split()
        chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created = int(time.time())
        
        # Send initial chunk with role
        yield ChatCompletionChunk(
            id=chunk_id,
            created=created,
            model=model.name,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(
                        role=MessageRole.ASSISTANT
                    )
                )
            ]
        )
        
        # Send content chunks
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            
            content_chunk = word + (" " if i < len(words) - 1 else "")
            
            yield ChatCompletionChunk(
                id=chunk_id,
                created=created,
                model=model.name,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(
                            content=content_chunk
                        )
                    )
                ]
            )
        
        # Send final chunk with finish_reason
        yield ChatCompletionChunk(
            id=chunk_id,
            created=created,
            model=model.name,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(),
                    finish_reason="stop"
                )
            ]
        )
    
    def _generate_contextual_response(self, user_message: str, model_config: dict, model_name: str) -> str:
        """Generate contextual response based on user input"""
        import random
        
        message_lower = user_message.lower()
        base_response = model_config["base"]
        
        # Greeting detection
        if any(word in message_lower for word in ["你好", "hello", "hi", "嗨", "您好"]):
            return random.choice(self.response_templates["greeting"])
        
        # Programming detection
        if any(word in message_lower for word in ["编程", "代码", "programming", "code", "算法", "debug", "bug"]):
            if "编程" in model_config["capabilities"] or "代码" in model_config["capabilities"]:
                return random.choice(self.response_templates["programming"])
            else:
                return f"{base_response}\n\n虽然我不是专门的编程模型，但我仍可以为您提供基础的编程帮助。"
        
        # Analysis detection
        if any(word in message_lower for word in ["分析", "analyze", "数据", "统计", "趋势"]):
            return random.choice(self.response_templates["analysis"])
        
        # Creative detection
        if any(word in message_lower for word in ["创意", "creative", "写作", "故事", "诗歌", "设计"]):
            return random.choice(self.response_templates["creative"])
        
        # Time query
        if any(word in message_lower for word in ["时间", "time", "现在", "今天", "日期"]):
            current_time = time.strftime('%Y年%m月%d日 %H:%M:%S')
            return f"{base_response}\n\n当前时间是：{current_time}。需要我帮您处理与时间相关的其他事务吗？"
        
        # Default intelligent response
        return self._generate_intelligent_response(user_message, model_config, model_name)
    
    def _generate_intelligent_response(self, user_message: str, model_config: dict, model_name: str) -> str:
        """Generate intelligent response for general queries"""
        import random
        
        responses = [
            f"根据您的问题「{user_message}」，我来为您详细分析和解答。\n\n{model_config['base']}\n\n我在{', '.join(model_config['capabilities'])}等方面具有专业能力，可以为您提供深入的帮助。",
            
            f"这是一个很有趣的问题！{model_config['base']}\n\n关于「{user_message}」，我可以从多个角度为您分析：\n\n1. 问题的核心要点\n2. 可能的解决方案\n3. 实施建议\n\n请告诉我您更关注哪个方面？",
            
            f"感谢您的信任！{model_config['base']}\n\n针对您提到的「{user_message}」，我建议我们可以这样来处理：\n\n• 首先理解问题的背景和目标\n• 然后分析可行的方法\n• 最后提供具体的实施步骤\n\n您觉得这个思路如何？",
        ]
        
        return random.choice(responses)
    
    def _add_context_awareness(self, messages: list, response: str) -> str:
        """Add conversation context awareness"""
        if len(messages) > 3:
            return f"基于我们之前的对话，{response}\n\n我注意到这是我们第{len(messages)//2}轮对话了，如果您有其他相关问题，我很乐意继续为您解答。"
        elif len(messages) == 3:
            return f"继续我们的讨论，{response}"
        else:
            return response