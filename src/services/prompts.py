"""
AI Prompt Templates
Centralized prompt management for all AI interactions
"""

class PromptTemplates:
    """Centralized prompt templates for AI interactions"""
    
    # Agent-specific prompts
    AGENTS = {
        'benchmarking': '''You are a benchmarking specialist. Analyze and compare the following data against industry standards. Provide specific metrics and recommendations.

Context: {context}

Please provide:
1. Key performance indicators
2. Industry comparisons
3. Recommendations for improvement''',
        
        'persona_generation': '''You are an expert in creating detailed user personas. Generate a comprehensive persona based on the following information.

Context: {context}

Please provide:
1. Demographics
2. Goals and motivations
3. Pain points
4. Behavioral patterns''',
        
        'data_analysis': '''You are a data analyst. Analyze the following data and provide actionable insights.

Context: {context}

Please provide:
1. Key findings
2. Trends and patterns
3. Statistical insights
4. Recommendations''',
        
        'report_writing': '''You are a professional report writer. Create a comprehensive, well-structured report on the following topic.

Context: {context}

Please provide:
1. Executive summary
2. Detailed analysis
3. Conclusions
4. Recommendations'''
    }
    
    # Task-related prompts
    TASKS = {
        'summarize': '''Please provide a concise summary of the following text. Focus on the main points and key takeaways.

Text to summarize:
{content}

Summary:''',
        
        'analyze': '''Analyze the following content and provide insights.

Content:
{content}

Analysis:''',
        
        'suggest_next_steps': '''Based on the following task information, suggest logical next steps.

Task: {title}
Description: {description}
Current Status: {status}

Suggested next steps:''',
        
        'extract_action_items': '''Extract action items from the following text.

Text:
{content}

Action items:'''
    }
    
    # Chat prompts
    CHAT = {
        'system': '''You are Alex, a helpful AI assistant for task management and productivity. You help users manage tasks, analyze data, and make informed decisions.''',
        
        'task_context': '''You are helping with the following task:

Title: {title}
Description: {description}
Status: {status}
Priority: {priority}

User question: {question}

Your response:''',
        
        'group_chat_context': '''You are participating in a group chat for the following task:

Task: {title}
Recent messages:
{messages}

User question: {question}

Your response:'''
    }
    
    # File analysis prompts
    FILES = {
        'analyze_document': '''Analyze the following document and provide key insights.

Filename: {filename}
Content:
{content}

Analysis:''',
        
        'extract_metadata': '''Extract relevant metadata from this document.

Filename: {filename}
Content:
{content}

Metadata:'''
    }
    
    @classmethod
    def get_agent_prompt(cls, agent_name, context):
        """Get formatted agent prompt"""
        agent_key = agent_name.lower().replace(' ', '_')
        template = cls.AGENTS.get(agent_key)
        if not template:
            raise ValueError(f'Unknown agent: {agent_name}')
        return template.format(context=context)
    
    @classmethod
    def get_task_prompt(cls, prompt_type, **kwargs):
        """Get formatted task prompt"""
        template = cls.TASKS.get(prompt_type)
        if not template:
            raise ValueError(f'Unknown task prompt: {prompt_type}')
        return template.format(**kwargs)
    
    @classmethod
    def get_chat_prompt(cls, prompt_type, **kwargs):
        """Get formatted chat prompt"""
        template = cls.CHAT.get(prompt_type)
        if not template:
            raise ValueError(f'Unknown chat prompt: {prompt_type}')
        return template.format(**kwargs)
    
    @classmethod
    def get_file_prompt(cls, prompt_type, **kwargs):
        """Get formatted file prompt"""
        template = cls.FILES.get(prompt_type)
        if not template:
            raise ValueError(f'Unknown file prompt: {prompt_type}')
        return template.format(**kwargs)
    
    @classmethod
    def list_agents(cls):
        """List available agents"""
        return list(cls.AGENTS.keys())
    
    @classmethod
    def list_task_prompts(cls):
        """List available task prompts"""
        return list(cls.TASKS.keys())

