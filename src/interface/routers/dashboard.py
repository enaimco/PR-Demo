"""Dashboard route — requires authentication."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.domain.ports import SessionPort
from src.infrastructure.session import GITHUB_USERNAME_KEY
from src.interface.dependencies import get_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def dashboard(
    request: Request,
    session: SessionPort = Depends(get_session),
) -> object:
    if not session.is_authenticated():
        return RedirectResponse(url="/login")
    github_username = session.get(GITHUB_USERNAME_KEY)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "github_username": github_username},
    )
