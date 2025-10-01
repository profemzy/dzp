"""
LangChain-based AI processor for conversation management and RAG
"""

import os
from typing import List, Dict, Any

import tiktoken
from langchain_core.messages import SystemMessage

from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class LangChainProcessor:
    """LangChain-based processor for conversation and RAG"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = None
        self.embeddings = None
        self.memory = InMemoryChatMessageHistory()
        self.vector_store = None
        self.retrieval_chain = None
        self.conversation_chain = None
        
        self.max_history_turns = 10
        self.max_tokens = 4000
        self.encoding = tiktoken.get_encoding("cl100k_base")  # For gpt-4
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LangChain components"""
        try:
            # Check if OpenAI API key is available
            if not self.config.openai_api_key:
                logger.warning("OpenAI API key not available, using fallback mode")
                self.llm = None
                self.embeddings = None
                return
            
            # Detect if using Azure OpenAI
            is_azure = "azure" in self.config.openai_model.lower() or "openai.azure.com" in (self.config.openai_base_url or "")
            
            if is_azure:
                # Initialize Azure OpenAI LLM
                self.llm = AzureChatOpenAI(
                    azure_deployment=self.config.openai_model.replace("azure/", ""),
                    openai_api_version="2024-02-15-preview",
                    temperature=0.1,
                    openai_api_key=self.config.openai_api_key,
                    azure_endpoint=self.config.openai_base_url
                )
                
                # Initialize Azure OpenAI Embeddings
                self.embeddings = AzureOpenAIEmbeddings(
                    azure_deployment="text-embedding-ada-002",
                    openai_api_version="2024-02-15-preview",
                    openai_api_key=self.config.openai_api_key,
                    azure_endpoint=self.config.openai_base_url
                )
            else:
                # Initialize standard OpenAI LLM
                self.llm = ChatOpenAI(
                    model=self.config.openai_model,
                    temperature=0.1,
                    openai_api_key=self.config.openai_api_key,
                    openai_api_base=self.config.openai_base_url
                )
                
                # Initialize embeddings using text-embedding-ada-002 as specified
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.config.openai_api_key,
                    openai_api_base=self.config.openai_base_url,
                    model="text-embedding-ada-002"
                )
            
            logger.info("LangChain components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain components: {e}")
            self.llm = None
            self.embeddings = None
    
    def create_knowledge_base(self, terraform_files: List[str]):
        """Create RAG knowledge base from Terraform files"""
        try:
            if not self.embeddings:
                logger.warning("Embeddings not available, skipping knowledge base creation")
                return
            
            documents = []
            
            # Load Terraform files
            for file_path in terraform_files:
                if os.path.exists(file_path):
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
            
            if not documents:
                logger.warning("No Terraform documents found for knowledge base")
                return
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            texts = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            # Create retrieval chain
            self._create_retrieval_chain()
            
            logger.info(f"Knowledge base created with {len(texts)} chunks from {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {e}")
            # Don't raise, just continue without RAG
    
    def _create_retrieval_chain(self):
        """Create RAG retrieval chain using modern LangChain syntax"""
        if not self.vector_store:
            return
        
        # Create contextualize question prompt
        contextualize_q_system_prompt = """Given a chat history and the latest user question 
        which might reference context in the chat history, formulate a standalone question 
        which can be understood without the chat history. Do NOT answer the question, 
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        # Create history aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            prompt=contextualize_q_prompt
        )
        
        # Create answer prompt
        system_prompt = """You are a Terraform infrastructure expert. Use the following context to answer the user's question about their Terraform configuration.

Context:
{context}

Provide a helpful and accurate answer about the Terraform infrastructure. If the context doesn't contain enough information, use your general knowledge about Terraform and cloud infrastructure.
"""
        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        # Create document chain
        question_answer_chain = create_stuff_documents_chain(self.llm, answer_prompt)
        
        # Create retrieval chain
        self.retrieval_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    def _create_conversation_chain(self):
        """Create general conversation chain using modern LangChain syntax"""
        template = """You are a helpful Terraform AI assistant. You help users understand and manage their Terraform infrastructure.

Chat History:
{chat_history}

Human: {input}

Assistant:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Use modern pipe syntax
        self.conversation_chain = prompt | self.llm
    
    async def process_query(self, query: str, use_rag: bool = True, project_data: Dict[str, Any] = None) -> str:
        """Process a user query with conversation context"""
        try:
            # If no LLM is available, use fallback with project data
            if not self.llm:
                return self._fallback_response(query, project_data)
            
            # Add user message to memory
            from langchain_core.messages import HumanMessage
            self.memory.add_message(HumanMessage(content=query))
            
            # Get effective history
            effective_history = self._get_effective_history()
            
            # Detect if this is a follow-up question
            is_followup = self._is_followup_question(query)
            
            # Check if this is a resource count question that can be answered with project data
            if project_data and self._is_resource_count_question(query):
                response = self._answer_resource_question(query, project_data)
            elif use_rag and self.retrieval_chain and (is_followup or self._needs_terraform_context(query)):
                # Use RAG for Terraform-specific queries
                result = await self.retrieval_chain.ainvoke({
                    "input": query,
                    "chat_history": effective_history
                })
                response = result.get("answer", "I couldn't process that query.")
            else:
                # Use general conversation chain
                if not self.conversation_chain:
                    self._create_conversation_chain()
                
                # For simple chain, use effective history
                effective_str = self._format_chat_history(effective_history)
                result = await self.conversation_chain.ainvoke({
                    "input": query,
                    "chat_history": effective_str
                })
                
                # Handle different response formats
                if hasattr(result, 'content'):
                    response = result.content
                elif isinstance(result, dict):
                    response = result.get("content", str(result))
                else:
                    response = str(result)
            
            # Add AI response to memory
            from langchain_core.messages import AIMessage
            self.memory.add_message(AIMessage(content=response))
            
            return response
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error processing your query: {str(e)}"
    
    def _get_effective_history(self) -> List:
        """Get effective history with summarization if too long"""
        full_history = self.memory.messages
        if len(full_history) <= self.max_history_turns * 2:
            return full_history
        
        # Summarize old history
        old_history = full_history[:-self.max_history_turns * 2]
        summary = self._summarize_history(old_history)
        
        recent_history = full_history[-self.max_history_turns * 2:]
        effective_history = [SystemMessage(content=f"Summary of previous conversation: {summary}")] + recent_history
        
        # Truncate if still over token limit
        effective_history = self._truncate_history(effective_history)
        
        return effective_history

    def _summarize_history(self, messages: List, max_turns: int = 5) -> str:
        """Summarize history using LLM"""
        if not self.llm:
            return "Previous conversation summary unavailable."
        
        # Format old messages for summarization
        formatted = []
        for msg in messages:
            role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        
        if len(formatted) == 0:
            return ""
        
        summary_prompt = ChatPromptTemplate.from_template(
            """Summarize the following conversation into key points relevant to Terraform infrastructure:
            
            Conversation:
            {conversation}
            
            Summary (keep under 200 words):"""
        )
        
        chain = summary_prompt | self.llm
        result = chain.invoke({"conversation": "\n".join(formatted[-10:])})  # Last 10 exchanges
        return result.content if hasattr(result, 'content') else str(result)

    def _truncate_history(self, history: List, max_tokens: int = None) -> List:
        """Truncate history to fit token limit"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        # Estimate tokens for entire prompt (approximate: history + system + query)
        # For simplicity, truncate to last N messages if over
        if len(history) > self.max_history_turns * 2:
            return history[-self.max_history_turns * 2:]
        
        # More precise: count tokens
        total_tokens = 0
        truncated = []
        for msg in reversed(history):
            msg_tokens = len(self.encoding.encode(str(msg)))
            if total_tokens + msg_tokens > max_tokens * 0.7:  # Leave room for query/system
                break
            truncated.insert(0, msg)
            total_tokens += msg_tokens
        
        return truncated
    
    def _format_chat_history(self, messages: List = None) -> str:
        """Format chat history for prompt"""
        if messages is None:
            messages = self.memory.messages
        
        history = []
        for message in messages:
            if hasattr(message, 'type'):
                if message.type == "human":
                    history.append(f"Human: {message.content}")
                elif message.type == "ai":
                    history.append(f"Assistant: {message.content}")
            else:
                # Fallback for different message types
                if isinstance(message, HumanMessage):
                    history.append(f"Human: {message.content}")
                elif isinstance(message, AIMessage):
                    history.append(f"Assistant: {message.content}")
                elif hasattr(message, 'content') and isinstance(message, SystemMessage):
                    history.append(f"System: {message.content}")
        return "\n".join(history)
    
    def _fallback_response(self, query: str, project_data: Dict[str, Any] = None) -> str:
        """Fallback response when OpenAI is not available"""
        query_lower = query.lower()
        
        # If we have project data, try to answer resource questions
        if project_data and self._is_resource_count_question(query):
            return self._answer_resource_question(query, project_data)
        
        # Simple pattern matching for common queries
        if "how many resources" in query_lower or "count resources" in query_lower:
            return "I can see you're asking about resource counts, but I need OpenAI API access to analyze your Terraform configuration. Please set up your OpenAI API key to get detailed information about your infrastructure."
        
        elif "what are they" in query_lower or "list them" in query_lower:
            return "I can see you're asking for more details, but I need OpenAI API access to provide specific information about your Terraform resources. Please set up your OpenAI API key to get detailed infrastructure analysis."
        
        elif "vm" in query_lower or "virtual machine" in query_lower:
            return "I can help you with virtual machine information, but I need OpenAI API access to analyze your Terraform configuration. Please set up your OpenAI API key to get VM details."
        
        elif "resource group" in query_lower:
            return "I can help you find resource group information, but I need OpenAI API access to analyze your Terraform configuration. Please set up your OpenAI API key to get resource group details."
        
        else:
            return "I'm a Terraform AI assistant, but I need OpenAI API access to help you with your infrastructure. Please set up your OpenAI API key in the .env file to enable full functionality. You can ask me about resources, plans, configurations, and more once the API is configured."
    
    def _is_resource_count_question(self, query: str) -> bool:
        """Check if the query is asking about resource counts"""
        query_lower = query.lower()
        resource_count_patterns = [
            "how many resources",
            "count resources",
            "number of resources",
            "total resources",
            "how many",
            "what resources",
            "list resources",
            "show resources"
        ]
        return any(pattern in query_lower for pattern in resource_count_patterns)
    
    def _answer_resource_question(self, query: str, project_data: Dict[str, Any]) -> str:
        """Answer resource-related questions using project data"""
        try:
            query_lower = query.lower()
            
            # Get resource information from project data
            resources = project_data.get('resources', {})
            
            # Handle the actual structure: {'count': 72, 'by_type': {...}, 'details': [...]}
            if isinstance(resources, dict):
                resource_count = resources.get('count', 0)
                resource_by_type = resources.get('by_type', {})
                resource_details = resources.get('details', [])
            else:
                # Fallback for unexpected structure
                resource_count = len(resources) if isinstance(resources, (list, dict)) else 0
                resource_by_type = {}
                resource_details = []
            
            if resource_count == 0:
                return "📊 **Resource Count:** I don't see any Terraform resources defined in your current configuration. Resources are defined using `resource` blocks in your .tf files."
            
            # Build response based on query type
            if "how many" in query_lower or "count" in query_lower or "number of" in query_lower:
                response = f"📊 **Resource Count:** You have **{resource_count}** Terraform resources defined in your configuration.\n\n"
                
                if resource_by_type:
                    response += "**Breakdown by type:**\n"
                    # Sort by count (descending)
                    sorted_types = sorted(resource_by_type.items(), key=lambda x: x[1], reverse=True)
                    for resource_type, count in sorted_types:
                        response += f"• {resource_type}: {count}\n"
                
                return response
            
            elif "what" in query_lower or "list" in query_lower or "show" in query_lower:
                response = f"📋 **Resource Overview:** You have **{resource_count}** Terraform resources:\n\n"
                
                if resource_by_type:
                    # Sort by count (descending)
                    sorted_types = sorted(resource_by_type.items(), key=lambda x: x[1], reverse=True)
                    for resource_type, count in sorted_types:
                        response += f"**{resource_type}** ({count} resources)\n"
                        
                        # Show examples from details if available
                        if resource_details:
                            examples = [detail['name'] for detail in resource_details if detail.get('type') == resource_type][:3]
                            for example in examples:
                                response += f"• {example}\n"
                            if count > len(examples):
                                response += f"• ... and {count - len(examples)} more\n"
                        response += "\n"
                
                return response
            
            else:
                # Generic resource response
                return f"📊 **Resources:** You have **{resource_count}** Terraform resources defined. Ask me 'what resources' or 'how many resources' for more details!"
                
        except Exception as e:
            logger.error(f"Error answering resource question: {e}")
            return "I had trouble analyzing your Terraform resources. Please try asking again or check your configuration files."
    
    def _is_followup_question(self, query: str) -> bool:
        """Detect if this is a follow-up question"""
        followup_indicators = [
            "what are they", "what is it", "tell me more", "show me", 
            "list them", "describe them", "details", "explain", 
            "what about", "how about", "and", "also", "those", "these"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in followup_indicators)
    
    def _needs_terraform_context(self, query: str) -> bool:
        """Check if query needs Terraform context"""
        terraform_keywords = [
            "resource", "terraform", "infrastructure", "vm", "virtual machine",
            "network", "storage", "provider", "variable", "output", "module",
            "plan", "apply", "destroy", "state", "configuration"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in terraform_keywords)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        history = []
        for message in self.memory.messages:
            if hasattr(message, 'type'):
                if message.type == "human":
                    history.append({"role": "user", "content": message.content})
                elif message.type == "ai":
                    history.append({"role": "assistant", "content": message.content})
            else:
                # Fallback for different message types
                if isinstance(message, HumanMessage):
                    history.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    history.append({"role": "assistant", "content": message.content})
        return history
    
    def enhance_query_with_context(self, query: str) -> str:
        """Enhance query with conversation context for better processing"""
        if not self.memory.messages:
            return query
        
        # Get recent conversation context
        recent_messages = self.memory.messages[-4:]  # Last 4 messages
        
        context_parts = []
        for msg in recent_messages:
            if hasattr(msg, 'type'):
                if msg.type == "human":
                    context_parts.append(f"Previous question: {msg.content}")
                elif msg.type == "ai":
                    context_parts.append(f"Previous answer: {msg.content}")
            else:
                # Fallback for different message types
                if isinstance(msg, HumanMessage):
                    context_parts.append(f"Previous question: {msg.content}")
                elif isinstance(msg, AIMessage):
                    context_parts.append(f"Previous answer: {msg.content}")
        
        if context_parts:
            enhanced_query = f"""
Conversation Context:
{' '.join(context_parts)}

Current Question: {query}

Please answer the current question considering the conversation context.
"""
            return enhanced_query
        
        return query
