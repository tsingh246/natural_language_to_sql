from typing import Any
from operator import itemgetter

from langchain_classic.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .db import create_db_connection
from .config import get_settings


def build_chain(settings=None) -> Any:
    settings = settings or get_settings()
    db = create_db_connection(settings)

    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=settings.OPENAI_TEMPERATURE)
    generate_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDatabaseTool(db=db)

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question in a friendly, concise way.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
    )

    answer = answer_prompt | llm | StrOutputParser()

    chain = (
        RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query") | execute_query
        )
        .assign(answer=answer)
    )
    return chain
