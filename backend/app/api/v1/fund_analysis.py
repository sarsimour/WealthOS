"""
Fund Analysis API Endpoints

FastAPI routes for fund portfolio analysis, image processing, and investment advisory.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.fund_analysis import (
    AdvisoryRequest,
    AdvisoryResponse,
    ImageAnalysisResponse,
)
from app.workflows.fund_advisory import analyze_fund_portfolio
from app.workflows.image_analysis import analyze_portfolio_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fund-analysis", tags=["fund-analysis"])


@router.post("/upload-image", response_model=ImageAnalysisResponse)
async def upload_portfolio_image(
    file: UploadFile = File(...), additional_context: Optional[str] = Form(None)
):
    """
    Upload and analyze a portfolio screenshot to extract fund holdings.

    Args:
        file: Portfolio screenshot image file (PNG, JPG, JPEG)
        additional_context: Optional additional context for analysis

    Returns:
        ImageAnalysisResponse: Extracted portfolio summary and metadata
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="File must be an image (PNG, JPG, JPEG)"
            )

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400, detail="File size must be less than 10MB"
            )

        # Analyze the image
        logger.info(f"Analyzing portfolio image: {file.filename}")

        portfolio_summary = await analyze_portfolio_image(
            image_data=file_content, additional_context=additional_context
        )

        # Create response
        response = ImageAnalysisResponse(
            success=True,
            portfolio_summary=portfolio_summary,
            message="Portfolio analysis completed successfully",
            processing_time=None,  # TODO: Add timing
        )

        logger.info(
            f"Image analysis completed: {len(portfolio_summary.holdings)} holdings extracted"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@router.post("/analyze-portfolio", response_model=AdvisoryResponse)
async def analyze_portfolio(request: AdvisoryRequest):
    """
    Analyze a portfolio and provide investment recommendations.

    Args:
        request: Portfolio analysis request with holdings and user profile

    Returns:
        AdvisoryResponse: Comprehensive portfolio analysis and recommendations
    """
    try:
        logger.info("Starting portfolio analysis")

        # Perform portfolio analysis
        portfolio_analysis = await analyze_fund_portfolio(
            portfolio_summary=request.portfolio_summary,
            user_profile=request.user_profile,
        )

        # Create response
        response = AdvisoryResponse(
            success=True,
            portfolio_analysis=portfolio_analysis,
            message="Portfolio analysis completed successfully",
            processing_time=None,  # TODO: Add timing
        )

        logger.info("Portfolio analysis completed successfully")

        return response

    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Portfolio analysis failed: {str(e)}"
        )


@router.post("/full-analysis", response_model=AdvisoryResponse)
async def full_portfolio_analysis(
    file: UploadFile = File(...),
    additional_context: Optional[str] = Form(None),
    user_profile: Optional[str] = Form(None),  # JSON string
):
    """
    Complete portfolio analysis: extract holdings from image and provide recommendations.

    Args:
        file: Portfolio screenshot image file
        additional_context: Optional context for image analysis
        user_profile: Optional user profile as JSON string

    Returns:
        AdvisoryResponse: Complete analysis with recommendations
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="File must be an image (PNG, JPG, JPEG)"
            )

        # Validate file size
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400, detail="File size must be less than 10MB"
            )

        logger.info(f"Starting full portfolio analysis for: {file.filename}")

        # Step 1: Extract holdings from image
        portfolio_summary = await analyze_portfolio_image(
            image_data=file_content, additional_context=additional_context
        )

        # Step 2: Parse user profile if provided
        parsed_user_profile = None
        if user_profile:
            try:
                import json

                parsed_user_profile = json.loads(user_profile)
            except json.JSONDecodeError:
                logger.warning("Invalid user profile JSON, proceeding without it")

        # Step 3: Perform portfolio analysis
        portfolio_analysis = await analyze_fund_portfolio(
            portfolio_summary=portfolio_summary, user_profile=parsed_user_profile
        )

        # Create response
        response = AdvisoryResponse(
            success=True,
            portfolio_analysis=portfolio_analysis,
            message="Full portfolio analysis completed successfully",
            processing_time=None,  # TODO: Add timing
        )

        logger.info("Full portfolio analysis completed successfully")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Full portfolio analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Full portfolio analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for fund analysis service."""
    return {"status": "healthy", "service": "fund-analysis", "version": "1.0.0"}


@router.get("/supported-formats")
async def get_supported_formats():
    """Get supported image formats and limits."""
    return {
        "supported_formats": ["image/png", "image/jpeg", "image/jpg"],
        "max_file_size": "10MB",
        "recommended_resolution": "1920x1080 or higher",
        "tips": [
            "Ensure fund names and codes are clearly visible",
            "Avoid screenshots with overlapping text",
            "Good lighting and contrast improve accuracy",
            "Include the complete holdings list in the screenshot",
        ],
    }
