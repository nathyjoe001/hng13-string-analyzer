# analyzer/views.py
import re
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import StringRecord
from .serializers import StringRecordSerializer
from .utils import analyze_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StringListCreateView(ListCreateAPIView):
    """
    POST /api/strings → Analyze and store a string.
    GET /api/strings → Retrieve all analyzed strings.
    """
    serializer_class = StringRecordSerializer
    queryset = StringRecord.objects.all()

    @swagger_auto_schema(
        operation_summary="Retrieve all analyzed strings",
        operation_description="Returns a list of all analyzed strings stored in the system.",
        responses={200: StringRecordSerializer(many=True)}
    )

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        try:
            if "is_palindrome" in params:
                v = params.get("is_palindrome").lower()
                if v not in ("true", "false"):
                    raise ValidationError("is_palindrome must be 'true' or 'false'")
                qs = qs.filter(is_palindrome=(v == "true"))
            if "min_length" in params:
                qs = qs.filter(length__gte=int(params.get("min_length")))
            if "max_length" in params:
                qs = qs.filter(length__lte=int(params.get("max_length")))
            if "word_count" in params:
                qs = qs.filter(word_count=int(params.get("word_count")))
            if "contains_character" in params:
                char = params.get("contains_character")
                if len(char) != 1:
                    raise ValidationError("contains_character must be a single character")
                qs = qs.filter(value__icontains=char)
            return qs
        except ValueError:
            raise ValidationError("Invalid query parameter values or types")


   

    @swagger_auto_schema(
        operation_summary="Create and analyze a new string",
        operation_description=(
            "This endpoint accepts a string input, analyzes it to compute properties "
            "such as length, palindrome status, unique characters, word count, and "
            "SHA256 hash. The analyzed string and its metadata are stored in the database."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'value': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The string to analyze',
                    example='hello'
                ),
            },
            required=['value']
        ),
        responses={
            201: openapi.Response(
                description="String analyzed and stored successfully",
                examples={
                    "application/json": {
                        "id": "473287f8298dba7163a897908958f7c0eae733e25d2e027992ea2edc9bed2fa8",
                        "value": "string",
                        "properties": {
                            "length": 6,
                            "is_palindrome": False,
                            "unique_characters": 6,
                            "word_count": 1,
                            "sha256_hash": "473287f8298dba7163a897908958f7c0eae733e25d2e027992ea2edc9bed2fa8",
                            "character_frequency_map": {
                                "s": 1,
                                "t": 1,
                                "r": 1,
                                "i": 1,
                                "n": 1,
                                "g": 1
                            }
                        },
                        "created_at": "2025-10-26T17:15:42.401421Z"
                    }
                }
            ),
            400: "Invalid request body",
        }
    )
    def create(self, request, *args, **kwargs):
        value = request.data.get("value", None)

        # 400 — missing value
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return Response(
                {"error": "Invalid request body or missing 'value' field"
                 }, status=status.HTTP_400_BAD_REQUEST)

        # 422 — not a string
        if not isinstance(value, str):
            return Response(
                {"error": "Invalid data type for 'value' (must be string)"}, 
                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # 409 — duplicate
        # Use sha256 to check existence OR value unique constraint
        props = analyze_string(value)
        sha = props["sha256_hash"]
        
        if StringRecord.objects.filter(id=sha).exists() or StringRecord.objects.filter(value=value).exists():
            return Response(
                {"error": "String already exists in the system"}, 
                status=status.HTTP_409_CONFLICT)

        # create and return the exact response shape
        record = StringRecord.objects.create(
            id=sha,
            value=value,
            length=props["length"],
            is_palindrome=props["is_palindrome"],
            unique_characters=props["unique_characters"],
            word_count=props["word_count"],
            sha256_hash=props["sha256_hash"],
            character_frequency_map=props["character_frequency_map"],
        )

        data = {
            "id": record.id,
            "value": record.value,
            "properties": props,
            "created_at": record.created_at.isoformat().replace("+00:00", "Z"),
        }
        return Response(data, status=status.HTTP_201_CREATED)

class StringDetailView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve a specific string and its analyzed properties by value.",
        manual_parameters=[
            openapi.Parameter(
                name="string_value",
                in_=openapi.IN_PATH,
                description="The string value you want to retrieve from the database.",
                type=openapi.TYPE_STRING,
                required=True,
                example="madam"
            )
        ],
        responses={
            200: openapi.Response(
                description="String found successfully.",
                examples={
                    "application/json": {
                        "id": "a7b3d19f...",
                        "value": "madam",
                        "properties": {
                            "length": 5,
                            "is_palindrome": True,
                            "unique_characters": 3,
                            "word_count": 1,
                            "sha256_hash": "a7b3d19f...",
                            "character_frequency_map": {"m": 2, "a": 2, "d": 1}
                        },
                        "created_at": "2025-10-25T12:00:00Z"
                    }
                }
            ),
            404: openapi.Response(
                description="String not found.",
                examples={"application/json": {"error": "String does not exist in the system"}}
            )
        }
    )
    def get(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"}, 
                status=status.HTTP_404_NOT_FOUND)
        serializer = StringRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a specific string by its value.",
        manual_parameters=[
            openapi.Parameter(
                name="string_value",
                in_=openapi.IN_PATH,
                description="The string value you want to delete from the database.",
                type=openapi.TYPE_STRING,
                required=True,
                example="madam"
            )
        ],
        responses={
            204: openapi.Response(
                description="String deleted successfully (no content returned)."
            ),
            404: openapi.Response(
                description="String not found.",
                examples={"application/json": {"error": "String does not exist in the system"}}
            )
        }
    )
    def delete(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"}, 
                status=status.HTTP_404_NOT_FOUND)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NaturalLanguageFilterView(APIView):
    """
    Filter strings using natural language queries such as:
    - "all single word palindromic strings"
    - "strings longer than 10 characters"
    - "strings containing the letter a"
    """

    # ✅ Swagger Documentation
    @swagger_auto_schema(
        operation_description="Filter strings using natural language queries (e.g. 'all single word palindromic strings').",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Natural language query (e.g. 'all palindromic strings', 'strings longer than 10 characters').",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Successfully filtered strings",
                examples={
                    "application/json": {
                        "data": [
                            {
                                "id": "abc123",
                                "value": "madam",
                                "length": 5,
                                "is_palindrome": True,
                                "word_count": 1,
                                "unique_characters": 3,
                                "sha256_hash": "a5d41402abc4b2a76b9719d911017c592",
                                "character_frequency_map": {"m": 2, "a": 2, "d": 1},
                                "created_at": "2025-10-25T12:00:00Z"
                            }
                        ],
                        "count": 1,
                        "interpreted_query": {
                            "original": "all single word palindromic strings",
                            "parsed_filters": {
                                "word_count": 1,
                                "is_palindrome": True
                            }
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid query parameter",
                examples={"application/json": {"error": "Query is required"}}
            ),
        }
    )
    def get(self, request):
        query = request.query_params.get("query", "")
        if not query or not query.strip():
            return Response({"error": "Query is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        parsed = {}
        ql = query.lower()

        if "palindromic" in ql:
            parsed["is_palindrome"] = True
        if "single word" in ql or "one word" in ql:
            parsed["word_count"] = 1
        if m := re.search(r"longer than (\d+)", ql):
            parsed["min_length"] = int(m.group(1)) + 1
        if m := re.search(r"shorter than (\d+)", ql):
            parsed["max_length"] = int(m.group(1)) - 1
        if m := re.search(r"letter ([a-z])", ql):
            parsed["contains_character"] = m.group(1)

        if not parsed:
            return Response(
                {"error": "Unable to parse natural language query"},
                  status=status.HTTP_400_BAD_REQUEST)

        qs = StringRecord.objects.all()
        if parsed.get("is_palindrome"):
            qs = qs.filter(is_palindrome=True)
        if parsed.get("word_count"):
            qs = qs.filter(word_count=parsed["word_count"])
        if parsed.get("min_length"):
            qs = qs.filter(length__gte=parsed["min_length"])
        if parsed.get("max_length"):
            qs = qs.filter(length__lte=parsed["max_length"])
        if parsed.get("contains_character"):
            qs = qs.filter(value__icontains=parsed["contains_character"])

        serializer = StringRecordSerializer(qs, many=True)
        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed
            }
        }, status=status.HTTP_200_OK)
