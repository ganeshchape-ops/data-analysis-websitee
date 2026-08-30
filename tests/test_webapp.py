"""
Web Application Route and Endpoint Test Suite
"""

import unittest
import os
import json
from app import app, DATA_FOLDER


class TestWebAppRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Performance Analytics Engine", response.data)

    def test_clean_demo_route(self):
        response = self.client.get("/demo/clean", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cohort Performance Analytics Dashboard", response.data)
        self.assertIn(b"Section Performance Comparison", response.data)

    def test_dirty_demo_route(self):
        response = self.client.get("/demo/dirty", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Data Health Score", response.data)

    def test_excel_export_route(self):
        # Load demo first
        self.client.get("/demo/clean")
        response = self.client.get("/export/excel")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertGreater(len(response.data), 0)
        response.close()

    def test_csv_export_route(self):
        self.client.get("/demo/clean")
        response = self.client.get("/export/csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/csv; charset=utf-8")
        self.assertGreater(len(response.data), 0)
        response.close()

    def test_api_analysis_endpoint(self):
        self.client.get("/demo/clean")
        response = self.client.get("/api/analysis")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("overall_stats", data)
        self.assertIn("section_summary", data)
        self.assertIn("subject_summary", data)
        self.assertIn("quality_summary", data)
        self.assertEqual(len(data["subject_summary"]), 6)
        response.close()


if __name__ == "__main__":
    unittest.main()
