#i am rewriting this cod
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')
logger = logging.getLogger(__name__)
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
# Load environment variables

logger.info("Environment variables loaded")

# Ensure API key is set
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY is required")


# Define the data model
class MCQ(BaseModel):
    question: str  
    options: List[str]  
    correct_answer: str  

class MCQList(BaseModel):
    mcqs: List[MCQ]# = Field(description="List of multiple choice questions")

def generate_mcqs(language):
    logger.info(f"Generating MCQs for {language} programming language")
    
    # Initialize the parser
    parser = PydanticOutputParser(pydantic_object=MCQList)
    
    # Create the prompt template with format instructions
    prompt_template = PromptTemplate(
        template="""
        Generate 10 multiple-choice questions (MCQs) on the programming language {language}.
        Each question should have four options (A, B, C, D), with one correct answer clearly indicated.
        
        {format_instructions}
        
        Ensure questions cover syntax, best practices, and key concepts.
        """,
        input_variables=["language"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Set up the model
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    logger.info("LLM initialized with gpt-3.5-turbo model")
    
    try:
        # Create and invoke the chain
        chain = prompt_template | llm | parser
        logger.info("Invoking LLM chain")
        
        result = chain.invoke({"language": language})
        logger.info(f"Successfully generated {len(result.mcqs)} MCQs")
        
        # Convert Pydantic models to dictionaries
        mcqs_dict = [mcq.model_dump() for mcq in result.mcqs]
        return mcqs_dict
    except Exception as e:
        logger.error(f"Error generating MCQs: {str(e)}", exc_info=True)
        if "API key" in str(e).lower():
            raise Exception("OpenAI API key is invalid or not set. Please check your .env file.")
        elif "model" in str(e).lower():
            raise Exception("Invalid model name. Please check the model configuration.")
        else:
            raise Exception(f"Failed to generate MCQs: {str(e)}")


