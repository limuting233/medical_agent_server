import asyncio

from langchain_core.messages import HumanMessage

from app.graph.graph import create_graph, init_checkpointer, init_store
from loguru import logger

async def main():
    await init_checkpointer()
    await init_store()
    graph = create_graph()

    config = {"configurable": {"thread_id": "123"}}
    # await graph.ainvoke(
    #     input={"messages": [HumanMessage(content="你好,我头痛")]},
    #     config={"configurable": {"thread_id": "123"}}
    # )

    state = await graph.aget_state(config=config)
    logger.info(state)



if __name__ == '__main__':
    asyncio.run(main())
