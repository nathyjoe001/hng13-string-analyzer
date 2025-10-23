import logging
import re
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import StringRecord
from .serializers import StringRecordSerializer
from .utils import analyze_string

logger = logging.getLogger('analyzer')


# ======================================================
# 1️⃣  Create new analyzed string
# ======================================================
class AnalyzeStringView(APIView):
    @swagger_auto_schema(
        operation_description="Handles creation of new analyzed strings (POST).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'value': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='String to analyze'
                ),
            },
            required=['value'],
        ),
        responses={
            201: openapi.Response('Created', StringRecordSerializer),
            400: 'Invalid request body or missing "value" field',
            422: 'Invalid data type for "value" (must be string)',
            409: 'String already exists in the system'
        }
    )
    def post(self, request):
        value = request.data.get("value")

        # 400 — Missing 'value' field
        if value is None or str(value).strip() == "":
            return Response(
                {"error": "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 422 — Wrong data type
        if not isinstance(value, str):
            return Response(
                {"error": "Invalid data type for 'value' (must be string)"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # 409 — Already exists
        if StringRecord.objects.filter(value=value).exists():
            return Response(
                {"error": "String already exists in the system"},
                status=status.HTTP_409_CONFLICT
            )

        # Analyze and store
        props = analyze_string(value)
        record = StringRecord.objects.create(
            value=value,
            length=props["length"],
            is_palindrome=props["is_palindrome"],
            unique_characters=props["unique_characters"],
            word_count=props["word_count"],
            character_frequency_map=props["character_frequency_map"],
        )

        serializer = StringRecordSerializer(record)
        logger.info(f"Analyzed new string: {value}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ======================================================
# 2️⃣  Retrieve or delete specific string
# ======================================================
class StringDetailView(APIView):
    """Retrieve or delete a specific analyzed string"""

    @swagger_auto_schema(
        operation_description="Get details for a specific string by its value.",
        responses={
            200: openapi.Response('OK', StringRecordSerializer),
            404: 'String does not exist in the system',
        }
    )
    def get(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StringRecordSerializer(record)
        logger.info(f"Retrieved string: {string_value}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific analyzed string by its value.",
        responses={
            204: 'String deleted successfully',
            404: 'String does not exist in the system'
        }
    )
    def delete(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"},
                status=status.HTTP_404_NOT_FOUND
            )

        record.delete()
        logger.warning(f"Deleted string: {string_value}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================================================
# 3️⃣  Get all strings with query filtering
# ======================================================
class StringListView(ListAPIView):
    serializer_class = StringRecordSerializer

    @swagger_auto_schema(
        operation_description="Retrieve all analyzed strings with optional filters.",
        manual_parameters=[
            openapi.Parameter(
                'is_palindrome', openapi.IN_QUERY,
                description="Filter by palindrome (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'min_length', openapi.IN_QUERY,
                description="Minimum string length",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'max_length', openapi.IN_QUERY,
                description="Maximum string length",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'word_count', openapi.IN_QUERY,
                description="Exact word count",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'contains_character', openapi.IN_QUERY,
                description="Filter by presence of character (single letter)",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response('Success', StringRecordSerializer(many=True)),
            400: 'Invalid query parameter values or types'
        }
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        filters_applied = {k: v for k, v in request.query_params.items()}
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "filters_applied": filters_applied
        })

    def get_queryset(self):
        queryset = StringRecord.objects.all()
        params = self.request.query_params

        try:
            if "is_palindrome" in params:
                val = params.get("is_palindrome").lower()
                if val not in ["true", "false"]:
                    raise ValidationError({"error": "is_palindrome must be true or false"})
                queryset = queryset.filter(is_palindrome=(val == "true"))

            if "min_length" in params:
                queryset = queryset.filter(length__gte=int(params.get("min_length")))

            if "max_length" in params:
                queryset = queryset.filter(length__lte=int(params.get("max_length")))

            if "word_count" in params:
                queryset = queryset.filter(word_count=int(params.get("word_count")))

            if "contains_character" in params:
                char = params.get("contains_character")
                if len(char) != 1:
                    raise ValidationError({"error": "contains_character must be a single character"})
                queryset = queryset.filter(value__icontains=char)

            return queryset

        except ValueError:
            raise ValidationError({"error": "Invalid query parameter values or types"})


# ======================================================
# 4️⃣  Natural Language Filtering
# ======================================================
class NaturalLanguageFilterView(APIView):
    @swagger_auto_schema(
        operation_description="Filter strings using natural language queries (e.g. 'all single word palindromic strings').",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Natural language query", type=openapi.TYPE_STRING),
        ],
        responses={
            200: "Success",
            400: "Unable to parse natural language query",
            422: "Query parsed but resulted in conflicting filters"
        }
    )
    def get(self, request):
        query = request.query_params.get("query", "")
        if not query.strip():
            return Response({"error": "Query is required"}, status=400)

        parsed_filters = {}
        q_lower = query.lower()

        # Heuristic parsing logic
        if "palindromic" in q_lower:
            parsed_filters["is_palindrome"] = True
        if "single word" in q_lower or "one word" in q_lower:
            parsed_filters["word_count"] = 1
        if match := re.search(r"longer than (\d+)", q_lower):
            parsed_filters["min_length"] = int(match.group(1)) + 1
        if match := re.search(r"shorter than (\d+)", q_lower):
            parsed_filters["max_length"] = int(match.group(1)) - 1
        if match := re.search(r"letter ([a-z])", q_lower):
            parsed_filters["contains_character"] = match.group(1)

        if not parsed_filters:
            return Response({"error": "Unable to parse natural language query"}, status=400)

        queryset = StringRecord.objects.all()
        if parsed_filters.get("is_palindrome"):
            queryset = queryset.filter(is_palindrome=True)
        if parsed_filters.get("word_count"):
            queryset = queryset.filter(word_count=parsed_filters["word_count"])
        if parsed_filters.get("min_length"):
            queryset = queryset.filter(length__gte=parsed_filters["min_length"])
        if parsed_filters.get("max_length"):
            queryset = queryset.filter(length__lte=parsed_filters["max_length"])
        if parsed_filters.get("contains_character"):
            queryset = queryset.filter(value__icontains=parsed_filters["contains_character"])

        serializer = StringRecordSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        })
