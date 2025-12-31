from fastapi import APIRouter

router = APIRouter()


@router.post("/stream")
async def chat_stream(request):
    """
    流式聊天接口
    :param request:
    :return:
    """
