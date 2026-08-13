import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER,
    TA_RIGHT,
    TA_JUSTIFY
)

class PDFReportGenerator:

    """
    Generates a structured PDF report for
    batch evaluation results.
    """

    def __init__(self):

        self.styles = getSampleStyleSheet()

        # -----------------------------
        # Title Style
        # -----------------------------

        self.title_style = self.styles["Heading1"]

        self.title_style.alignment = TA_CENTER

        self.title_style.textColor = colors.HexColor(
            "#4F46E5"
        )

        self.title_style.spaceAfter = 18

        # -----------------------------
        # Section Heading
        # -----------------------------

        self.heading_style = self.styles["Heading2"]

        self.heading_style.textColor = colors.HexColor(
            "#1F2937"
        )

        self.heading_style.spaceBefore = 6

        self.heading_style.spaceAfter = 10

        # -----------------------------
        # Normal Text
        # -----------------------------

        self.normal_style = self.styles["BodyText"]

        self.normal_style.leading = 18

        self.normal_style.spaceAfter = 6

        # --------------------------------
        # Executive Summary Text
        # --------------------------------

        self.summary_style = ParagraphStyle(

            "Summary",

            parent=self.styles["BodyText"],

            fontName="Helvetica",

            fontSize=11,

            leading=18,

            alignment=TA_JUSTIFY,

            textColor=colors.HexColor("#374151"),

            spaceAfter=8

        )

        # -----------------------------
        # Small Text
        # -----------------------------

        self.small_style = self.styles["BodyText"]

        self.small_style.fontSize = 9

        self.small_style.leading = 12

        # -----------------------------
        # Verdict Styles
        # -----------------------------

        self.pass_style = self.styles["BodyText"]

        self.pass_style.textColor = colors.green

        self.pass_style.fontName = "Helvetica-Bold"


        self.warning_style = self.styles["BodyText"]

        self.warning_style.textColor = colors.orange

        self.warning_style.fontName = "Helvetica-Bold"


        self.fail_style = self.styles["BodyText"]

        self.fail_style.textColor = colors.red

        self.fail_style.fontName = "Helvetica-Bold"


    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _safe(self, value):

        """
        Return a printable value.
        """

        if value is None:
            return "-"

        if value == "":
            return "-"

        return str(value)


    def _score(self, value):

        """
        Format score values.
        """

        if value is None:
            return "-"

        return f"{value}/10"


    def _verdict_style(self, verdict):

        """
        Return paragraph style
        according to verdict.
        """

        if verdict == "Pass":
            return self.pass_style

        if verdict == "Needs Improvement":
            return self.warning_style

        return self.fail_style


    def _section_title(
        self,
        story,
        title,
        alignment=TA_LEFT
    ):

        style = ParagraphStyle(
            "section_title",
            parent=self.heading_style,
            alignment=alignment
        )

        story.append(
            Paragraph(
                title,
                style
            )
        )

        self._horizontal_space(
            story,
            0.12
        )

    def _horizontal_space(
        self,
        story,
        height=0.18
    ):

        """
        Add vertical spacing.
        """

        story.append(

            Spacer(
                1,
                height * inch
            )

        )
    # ==========================================
    # RESPONSE HEADER
    # ==========================================

    def _response_header(
        self,
        story,
        row_number
    ):

        table = Table(

            [[
                f"Response #{row_number}"
            ]],

            colWidths=[6.2 * inch]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#EEF2FF")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#4338CA")
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,-1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0,0),
                    (-1,-1),
                    15
                ),

                ("ALIGN", (0,0), (-1,0), "CENTER"),

                ("ALIGN", (1,1), (1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.HexColor("#C7D2FE")
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.08
        )


    # ==========================================
    # INFORMATION CARD
    # ==========================================

    def _info_card(
        self,
        story,
        title,
        text
    ):

        title_paragraph = Paragraph(

            f"<b>{title}</b>",

            ParagraphStyle(

                "card_title",

                parent=self.small_style,

                textColor=colors.HexColor("#1E3A8A"),

                spaceAfter=4

            )

        )

        body = Paragraph(

            self._safe(text),

            ParagraphStyle(

                "card_body",

                parent=self.small_style,

                textColor=colors.HexColor("#374151"),

                leading=15

            )

        )

        table = Table(

            [[
                title_paragraph
            ],
            [
                body
            ]],

            colWidths=[6.2 * inch]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.HexColor("#F8FAFC")
                ),

                (
                    "BACKGROUND",
                    (0,1),
                    (-1,1),
                    colors.white
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.HexColor("#E5E7EB")
                ),

                (
                    "LINEBELOW",
                    (0,0),
                    (-1,0),
                    0.3,
                    colors.HexColor("#E5E7EB")
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "RIGHTPADDING",
                    (0,0),
                    (-1,-1),
                    10
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.08
        )

    # ==========================================
    # VERDICT BADGE
    # ==========================================

    def _verdict_badge(
        self,
        story,
        verdict
    ):

        # --------------------------------------
        # Badge Colors
        # --------------------------------------

        if verdict == "Pass":

            bg = "#DCFCE7"
            border = "#22C55E"
            fg = "#166534"

        elif verdict == "Needs Improvement":

            bg = "#FEF3C7"
            border = "#F59E0B"
            fg = "#92400E"

        else:

            bg = "#FEE2E2"
            border = "#EF4444"
            fg = "#991B1B"

        # --------------------------------------
        # Badge Table
        # --------------------------------------

        badge = Table(

            [[

                Paragraph(

                    f"<b>{verdict}</b>",

                    ParagraphStyle(

                        "badge",

                        parent=self.small_style,

                        alignment=TA_CENTER,

                        textColor=colors.HexColor(fg),

                        fontSize=12,

                        leading=14

                    )

                )

            ]],

            colWidths=[6.2 * inch]

        )

        # --------------------------------------
        # Styling
        # --------------------------------------

        badge.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(bg)
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.HexColor(border)
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                )

            ])

        )

        story.append(
            badge
        )

        self._horizontal_space(
            story,
            0.12
        )

    # ==========================================
    # ERROR BOX
    # ==========================================

    def _error_box(
        self,
        story,
        message
    ):

        title = Paragraph(

            "<font color='#16A34A'><b>Evaluation Failed</b></font>",

            self.heading_style

        )

        description = Paragraph(

            "The response could not be evaluated because an exception "
            "occurred during the evaluation pipeline.",

            self.small_style

        )

        reason = Paragraph(

            f"<b>Error Details</b><br/><br/>{self._safe(message)}",

            self.small_style

        )

        recommendation = Paragraph(

            "<b>Recommended Action</b><br/><br/>"
            "Verify the input data, API connectivity and evaluation "
            "configuration before retrying the evaluation.",

            self.small_style

        )

        table = Table(

            [

                [title],

                [description],

                [reason],

                [recommendation]

            ],

            colWidths=[6.2*inch]

        )

        table.setStyle(

            TableStyle([

                ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FEF2F2")),

                ("BOX",(0,0),(-1,-1),0.8,colors.HexColor("#EF4444")),

                ("LINEBELOW",(0,0),(-1,0),0.6,colors.HexColor("#FCA5A5")),

                ("BOTTOMPADDING",(0,0),(-1,-1),10),

                ("TOPPADDING",(0,0),(-1,-1),10),

                ("LEFTPADDING",(0,0),(-1,-1),12),

                ("RIGHTPADDING",(0,0),(-1,-1),12)

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.12
        )

    # ==========================================
    # SCORE TABLE
    # ==========================================

    def _score_table(
        self,
        story,
        evaluation
    ):

        score_data = [

            ["Dimension", "Score"],

            [
                "Relevance",
                self._score(
                    evaluation["relevance"]["score"]
                )
            ],

            [
                "Accuracy",
                self._score(
                    evaluation["accuracy"]["score"]
                )
            ],

            [
                "Hallucination",
                self._score(
                    evaluation["hallucination"]["score"]
                )
            ],

            [
                "Completeness",
                self._score(
                    evaluation["completeness"]["score"]
                )
            ],

            [
                "Overall",
                self._score(
                    evaluation["overall_score"]
                )
            ]

        ]

        table = Table(

            score_data,

            colWidths=[
                4.2 * inch,
                1.6 * inch
            ]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.HexColor("#4F46E5")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "BACKGROUND",
                    (0,1),
                    (-1,1),
                    colors.HexColor("#FFFFFF")
                ),

                (
                    "BACKGROUND",
                    (0,2),
                    (-1,2),
                    colors.HexColor("#F8FAFC")
                ),

                (
                    "BACKGROUND",
                    (0,3),
                    (-1,3),
                    colors.HexColor("#FFFFFF")
                ),

                (
                    "BACKGROUND",
                    (0,4),
                    (-1,4),
                    colors.HexColor("#F8FAFC")
                ),

                (
                    "BACKGROUND",
                    (0,5),
                    (-1,5),
                    colors.HexColor("#EEF2FF")
                ),

                (
                    "FONTNAME",
                    (0,5),
                    (-1,5),
                    "Helvetica-Bold"
                ),

                ("ALIGN", (0,0), (-1,0), "CENTER"),

                ("ALIGN", (1,1), (1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.4,
                    colors.HexColor("#D1D5DB")
                ),

                (
                    "ALIGN",
                    (1,1),
                    (1,-1),
                    "CENTER"
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    8
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.10
        )


    # ==========================================
    # UNSUPPORTED CLAIMS
    # ==========================================

    def _unsupported_claims(
        self,
        story,
        claims
    ):

        if not claims:
            return

        title = Paragraph(

            "<b>Unsupported Claims</b>",

            ParagraphStyle(

                "unsupported_title",

                parent=self.small_style,

                textColor=colors.HexColor("#4B5563")

            )

        )

        rows = [[title]]

        for claim in claims:

            rows.append(

                [

                    Paragraph(

                        "• " + self._safe(claim),

                        self.small_style

                    )

                ]

            )

        table = Table(

            rows,

            colWidths=[6.2 * inch]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#FFFBEB")
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.HexColor("#FCD34D")
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    10
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.10
        )


    # ==========================================
    # VERDICT SUMMARY BOX
    # ==========================================

    def _summary_box(
        self,
        story,
        summary
    ):

        if not summary:
            return

        table = Table(

            [

                [

                    Paragraph(

                        "<b>Evaluation Summary</b>",

                        ParagraphStyle(

                            "summary_title",

                            parent=self.small_style,

                            textColor=colors.HexColor("#1D4ED8")

                        )

                    )

                ],

                [

                    Paragraph(

                        self._safe(summary),

                        self.small_style

                    )

                ]

            ],

            colWidths=[6.2 * inch]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    colors.HexColor("#EFF6FF")
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.HexColor("#93C5FD")
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    8
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    10
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.12
        )

    # ==========================================
    # COVER PAGE
    # ==========================================

    def _add_cover_page(
        self,
        story,
        batch_results
    ):

        # ==========================================
        # MAIN TITLE
        # ==========================================

        story.append(
            Spacer(1, 0.35 * inch)
        )

        story.append(

            Paragraph(

                "<font color='#4338CA'><b>"
                "AI Response Quality Evaluator"
                "</b></font>",

                ParagraphStyle(

                    "cover_title",

                    parent=self.styles["Title"],

                    alignment=TA_CENTER,

                    fontSize=28,

                    leading=32,

                    spaceAfter=8

                )

            )

        )

        # ==========================================
        # REPORT TYPE
        # ==========================================

        story.append(

            Paragraph(

                "<font color='#4F46E5' size='18'>"
                "<b>Batch Evaluation Report</b>"
                "</font>",

                ParagraphStyle(

                    "subtitle",

                    parent=self.styles["Heading2"],

                    alignment=TA_CENTER,

                    spaceAfter=24

                )

            )

        )

        # ==========================================
        # DESCRIPTION
        # ==========================================

        description = (
            "This report presents an automated quality assessment of "
            "AI-generated responses using a multi-agent evaluation "
            "framework. Each response is independently analyzed across "
            "four quality dimensions before producing an overall verdict."
        )

        story.append(

            Paragraph(

                description,

                ParagraphStyle(

                    "description",

                    parent=self.normal_style,

                    alignment=TA_CENTER,

                    textColor=colors.HexColor("#4B5563"),

                    leading=20,

                    spaceAfter=28

                )

            )

        )

        # ==========================================
        # INFORMATION TABLE
        # ==========================================

        generated_time = datetime.now().strftime(
            "%d %B %Y, %I:%M %p"
        )

        info_data = [

            ["Generated On", generated_time],

            ["Report Type", "Batch Evaluation"],

            ["Evaluation Engine", "Multi-Agent LLM Evaluator"],

            ["Framework", "Retrieval-Augmented Generation (RAG)"],

            ["LLM Provider", "Groq"],

        ]

        info_table = Table(

            info_data,

            colWidths=[2.2 * inch, 3.6 * inch]

        )

        info_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),

                ("BACKGROUND", (1, 0), (1, -1), colors.white),

                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#243B53")),

                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),

                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),

                ("TOPPADDING", (0, 0), (-1, -1), 10),

                ("LEFTPADDING", (0, 0), (-1, -1), 10),

            ])

        )

        story.append(info_table)

        story.append(
            Spacer(1, 0.30 * inch)
        )

        # ==========================================
        # REPORT SUMMARY
        # ==========================================

        summary_data = [

            [

                "Total Responses",

                "Average Score"

            ],

            [

                str(batch_results["total_rows"]),

                f'{batch_results["average_score"]:.1f}/10'

            ],

            [

                "Pass",

                "Needs Improvement"

            ],

            [

                str(batch_results["verdict_counts"]["Pass"]),

                str(batch_results["verdict_counts"]["Needs Improvement"])

            ]

        ]

        summary_table = Table(

            summary_data,

            colWidths=[2.9 * inch, 2.9 * inch]

        )

        summary_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEF2FF")),

                ("BACKGROUND", (0,2), (-1,2), colors.HexColor("#EEF2FF")),

                ("BACKGROUND", (0,1), (-1,1), colors.white),

                ("BACKGROUND", (0,3), (-1,3), colors.white),

                ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#243B53")),

                ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),

                ("FONTSIZE", (0,1), (-1,1), 18),

                ("FONTSIZE", (0,3), (-1,3), 18),

                ("ALIGN", (0,0), (-1,-1), "CENTER"),

                ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D1D5DB")),

                ("BOTTOMPADDING", (0,0), (-1,-1), 12),

                ("TOPPADDING", (0,0), (-1,-1), 12)

            ])

        )

        story.append(summary_table)

        story.append(
            Spacer(1, 0.25 * inch)
        )

        # ==========================================
        # EVALUATION DIMENSIONS
        # ==========================================

        story.append(

            Paragraph(

                "<b>Evaluation Dimensions</b>",

                self.heading_style

            )

        )

        dimensions = [

            "✓ Relevance",

            "✓ Accuracy",

            "✓ Hallucination Detection",

            "✓ Completeness"

        ]

        for item in dimensions:

            story.append(

                Paragraph(

                    f"<font color='#16A34A'>{item}</font>",

                    self.normal_style

                )

            )

        story.append(
            Spacer(1, 0.30 * inch)
        )

        # ==========================================
        # FOOTER NOTE
        # ==========================================

        story.append(

            Paragraph(

                "<font color='#6B7280'>"
                "This report was generated automatically by the "
                "<b>AI Response Quality Evaluator</b>."
                "</font>",

                ParagraphStyle(

                    "footer",

                    parent=self.small_style,

                    alignment=TA_CENTER,

                    leading=18

                )

            )

        )

        story.append(
            Spacer(1, 0.03 * inch)
        )

        story.append(PageBreak())

    # ==========================================
    # EXECUTIVE SUMMARY
    # ==========================================

    def _add_executive_summary(
        self,
        story,
        batch_results
    ):

        analytics = batch_results["analytics"]

        # --------------------------------------
        # TITLE
        # --------------------------------------

        story.append(

            Paragraph(

                "Executive Summary",

                self.title_style

            )

        )

        story.append(

            Paragraph(

                "This report presents the overall performance of the AI Response "
                "Validation System with Hallucination Detection Assistance. "
                "The submitted responses were evaluated using multiple specialized "
                "agents to measure relevance, accuracy, hallucination detection "
                "and completeness before generating an overall quality verdict.",

                self.summary_style

            )

        )

        story.append(
            Spacer(1, 0.03 * inch)
        )

        # --------------------------------------
        # BATCH STATISTICS
        # --------------------------------------

        story.append(

            Paragraph(

                "<b>Batch Statistics</b>",

                self.heading_style

            )

        )

        stats_table = Table(

            [

                ["Metric", "Value"],

                ["Total Responses",
                batch_results["total_rows"]],

                ["Successfully Evaluated",
                batch_results["successful_rows"]],

                ["Average Score",
                f'{batch_results["average_score"]:.2f}/10'],

                ["Pass",
                batch_results["verdict_counts"]["Pass"]],

                ["Needs Improvement",
                batch_results["verdict_counts"]["Needs Improvement"]],

                ["Fail",
                batch_results["verdict_counts"]["Fail"]]

            ],

            colWidths=[3.6 * inch, 2.0 * inch]

        )

        stats_table.setStyle(

            TableStyle([

                ("BACKGROUND",
                (0,0),(-1,0),
                colors.HexColor("#4F46E5")),

                ("TEXTCOLOR",
                (0,0),(-1,0),
                colors.white),

                ("FONTNAME",
                (0,0),(-1,0),
                "Helvetica-Bold"),

                ("BACKGROUND",
                (0,1),(-1,-1),
                colors.whitesmoke),

                ("ALIGN", (0,0), (-1,0), "CENTER"),

                ("ALIGN", (1,1), (1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                ("GRID",
                (0,0),(-1,-1),
                0.4,
                colors.HexColor("#D1D5DB")),

                ("BOTTOMPADDING",
                (0,0),(-1,0),
                10)

            ])

        )

        story.append(stats_table)

        story.append(
            Spacer(1, 0.09 * inch)
        )

        # --------------------------------------
        # DIMENSION SUMMARY
        # --------------------------------------

        story.append(

            Paragraph(

                "<b>Dimension-wise Performance</b>",

                self.heading_style

            )

        )

        analytics_table = Table(

            [

                ["Dimension", "Average Score"],

                ["Relevance",
                self._score(analytics["average_relevance"])],

                ["Accuracy",
                self._score(analytics["average_accuracy"])],

                ["Hallucination",
                self._score(analytics["average_hallucination"])],

                ["Completeness",
                self._score(analytics["average_completeness"])]

            ],

            colWidths=[3.6 * inch, 2.0 * inch]

        )

        analytics_table.setStyle(

            TableStyle([

                ("BACKGROUND",
                (0,0),(-1,0),
                colors.HexColor("#4F46E5")),

                ("TEXTCOLOR",
                (0,0),(-1,0),
                colors.white),

                ("FONTNAME",
                (0,0),(-1,0),
                "Helvetica-Bold"),

                ("BACKGROUND",
                (0,1),(-1,-1),
                colors.HexColor("#F8FAFC")),

                ("ALIGN", (0,0), (-1,0), "CENTER"),

                ("ALIGN", (1,1), (1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                ("GRID",
                (0,0),(-1,-1),
                0.4,
                colors.HexColor("#D1D5DB"))

            ])

        )

        story.append(analytics_table)

        story.append(
            Spacer(1, 0.09 * inch)
        )

        # --------------------------------------
        # KEY FINDINGS
        # --------------------------------------

        story.append(

            Paragraph(

                "<b>Key Findings</b>",

                self.heading_style

            )

        )

        findings = [

            f"• Average Overall Score: <b>{batch_results['average_score']:.2f}/10</b>",

            f"• Best Performing Dimension: <b>{analytics['best_dimension']}</b>",

            f"• Weakest Dimension: <b>{analytics['weakest_dimension']}</b>",

            f"• Hallucination Frequency: <b>{analytics['hallucination_frequency']:.1f}%</b>",

            f"• Highest Response Score: <b>{self._score(analytics['highest_score'])}</b>",

            f"• Lowest Response Score: <b>{self._score(analytics['lowest_score'])}</b>"

        ]

        for item in findings:

            story.append(

                Paragraph(

                    item,

                    self.summary_style

                )

            )

        story.append(
            Spacer(1, 0.09 * inch)
        )

        # --------------------------------------
        # OVERALL ASSESSMENT
        # --------------------------------------

        story.append(

            Paragraph(

                "<b>Overall Assessment</b>",

                self.heading_style

            )

        )

        average = batch_results["average_score"]

        if average >= 8:

            assessment = (
                "The evaluated responses demonstrate strong overall quality "
                "with high factual consistency, effective grounding, and good "
                "coverage of the user's queries."
            )

        elif average >= 6:

            assessment = (
                "The evaluated responses demonstrate satisfactory overall "
                "quality. While most responses are relevant and factually "
                "reasonable, improvements are recommended in weaker evaluation "
                "dimensions to further increase response reliability."
            )

        else:

            assessment = (
                "The overall response quality is below the desired level. "
                "Significant improvements are recommended in factual grounding, "
                "response completeness, and hallucination reduction."
            )

        story.append(

            Paragraph(

                assessment,

                self.summary_style

            )

        )

        story.append(PageBreak())

    # ==========================================
    # BATCH ANALYTICS
    # ==========================================

    def _add_batch_analytics(
        self,
        story,
        batch_results
    ):

        analytics = batch_results.get(
            "analytics",
            {}
        )

        self._section_title(
            story,
            "Batch Analytics"
        )

        analytics_data = [

            [
                "Metric",
                "Value"
            ],

            [
                "Average Relevance",
                self._score(
                    analytics.get(
                        "average_relevance"
                    )
                )
            ],

            [
                "Average Accuracy",
                self._score(
                    analytics.get(
                        "average_accuracy"
                    )
                )
            ],

            [
                "Average Hallucination",
                self._score(
                    analytics.get(
                        "average_hallucination"
                    )
                )
            ],

            [
                "Average Completeness",
                self._score(
                    analytics.get(
                        "average_completeness"
                    )
                )
            ],

            [
                "Highest Overall Score",
                self._score(
                    analytics.get(
                        "highest_score"
                    )
                )
            ],

            [
                "Lowest Overall Score",
                self._score(
                    analytics.get(
                        "lowest_score"
                    )
                )
            ],

            [
                "Best Performing Dimension",
                self._safe(
                    analytics.get(
                        "best_dimension"
                    )
                )
            ],

            [
                "Weakest Dimension",
                self._safe(
                    analytics.get(
                        "weakest_dimension"
                    )
                )
            ],

            [
                "Hallucination Frequency",
                f'{analytics.get("hallucination_frequency",0)}%'
            ],

            [
                "Grounded Responses",
                analytics.get(
                    "responses_without_hallucinations",
                    0
                )
            ]

        ]

        table = Table(

            analytics_data,

            colWidths=[
                3.4 * inch,
                2.3 * inch
            ]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.HexColor("#4F46E5")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "BACKGROUND",
                    (0,1),
                    (-1,-1),
                    colors.whitesmoke
                ),

                ("ALIGN", (0,0), (-1,0), "CENTER"),

                ("ALIGN", (1,1), (1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.grey
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,0),
                    10
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.3
        )

    # ==========================================
    # VERDICT DISTRIBUTION
    # ==========================================

    def _add_verdict_distribution(
        self,
        story,
        batch_results
    ):

        verdicts = batch_results.get(
            "verdict_counts",
            {}
        )

        analytics = batch_results.get(
            "analytics",
            {}
        )

        self._section_title(
            story,
            "Verdict Distribution"
        )

        data = [

            [
                "Verdict",
                "Count",
                "Percentage"
            ],

            [

                "Pass",

                verdicts.get(
                    "Pass",
                    0
                ),

                f'{analytics.get("pass_percentage",0)}%'

            ],

            [

                "Needs Improvement",

                verdicts.get(
                    "Needs Improvement",
                    0
                ),

                f'{analytics.get("needs_improvement_percentage",0)}%'

            ],

            [

                "Fail",

                verdicts.get(
                    "Fail",
                    0
                ),

                f'{analytics.get("fail_percentage",0)}%'

            ]

        ]

        table = Table(

            data,

            colWidths=[
                3.2*inch,
                1.2*inch,
                1.3*inch
            ]

        )

        table.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.HexColor("#4F46E5")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0,1),
                    (-1,-1),
                    colors.beige
                ),

                (
                    "ALIGN",
                    (1,1),
                    (-1,-1),
                    "CENTER"
                )

            ])

        )

        story.append(table)

        self._horizontal_space(
            story,
            0.3
        )

    # ==========================================
    # BATCH SUMMARY
    # ==========================================

    def _add_batch_summary(
        self,
        story,
        batch_results
    ):

        analytics = batch_results.get(
            "analytics",
            {}
        )

        summary = f"""

<b>Summary</b><br/><br/>

A total of
<b>{batch_results.get("total_rows",0)}</b>
responses were processed.

<b>{batch_results.get("successful_rows",0)}</b>
responses completed successfully.

The average overall evaluation score was
<b>{self._score(batch_results.get("average_score"))}</b>.

The strongest evaluation dimension was
<b>{self._safe(analytics.get("best_dimension"))}</b>,
while the weakest was
<b>{self._safe(analytics.get("weakest_dimension"))}</b>.

The detected hallucination frequency across
the successfully evaluated responses was

<b>{analytics.get("hallucination_frequency",0)}%</b>.

"""

        story.append(

            Paragraph(

                summary,

                self.summary_style

            )

        )

        story.append(PageBreak())

    # ==========================================
    # INDIVIDUAL EVALUATION RESULTS
    # ==========================================

    def _add_individual_results(
        self,
        story,
        batch_results
    ):

        self._section_title(

            story,

            "Individual Evaluation Results",

            alignment=TA_CENTER

        )

        results = batch_results.get(

            "results",

            []

        )

        if not results:

            story.append(

                Paragraph(

                    "No evaluation results available.",

                    self.normal_style

                )

            )

            return

        for result in results:

            row_number = result.get(

                "row_number",

                "-"

            )

            status = result.get(

                "status",

                "error"

            )

            # ----------------------------------
            # RESPONSE HEADER
            # ----------------------------------

            self._response_header(

                story,

                row_number

            )

            # ----------------------------------
            # QUESTION
            # ----------------------------------

            self._info_card(

                story,

                "Question",

                result.get("question")

            )

            # ----------------------------------
            # AI RESPONSE
            # ----------------------------------

            self._info_card(

                story,

                "AI Response",

                result.get("response")

            )

            # ----------------------------------
            # REFERENCE ANSWER
            # ----------------------------------

            if result.get("reference"):

                self._info_card(

                    story,

                    "Reference Answer",

                    result.get("reference")

                )

            # ----------------------------------
            # ERROR PAGE
            # ----------------------------------

            if status == "error":

                self._error_box(

                    story,

                    result.get("error")

                )

                story.append(

                    PageBreak()

                )

                continue

            evaluation = result.get(

                "evaluation",

                {}

            )

            # ----------------------------------
            # SCORE TABLE
            # ----------------------------------

            self._score_table(

                story,

                evaluation

            )

            # ----------------------------------
            # VERDICT
            # ----------------------------------

            self._verdict_badge(

                story,

                evaluation.get(

                    "verdict",

                    "-"

                )

            )

            # ----------------------------------
            # UNSUPPORTED CLAIMS
            # ----------------------------------

            unsupported = (

                evaluation

                .get(

                    "hallucination",

                    {}

                )

                .get(

                    "unsupported_claims",

                    []

                )

            )

            self._unsupported_claims(

                story,

                unsupported

            )

            # ----------------------------------
            # SUMMARY
            # ----------------------------------

            self._summary_box(

                story,

                evaluation.get(

                    "verdict_summary",

                    ""

                )

            )

            # ----------------------------------
            # PAGE BREAK
            # ----------------------------------

            story.append(

                PageBreak()

            )
    # ==========================================
    # FLAGGED RESPONSES
    # ==========================================

    def _add_flagged_responses(
        self,
        story,
        batch_results
    ):

        self._section_title(
            story,
            "Flagged Responses"
        )

        results = batch_results.get(
            "results",
            []
        )

        flagged = []

        for result in results:

            if result.get("status") != "success":
                continue

            evaluation = result.get(
                "evaluation",
                {}
            )

            verdict = evaluation.get(
                "verdict"
            )

            unsupported = (
                evaluation
                .get(
                    "hallucination",
                    {}
                )
                .get(
                    "unsupported_claims",
                    []
                )
            )

            if (
                verdict != "Pass"
                or unsupported
            ):

                flagged.append(result)

        if not flagged:

            story.append(

                Paragraph(

                    "No responses were flagged during evaluation.",

                    self.normal_style

                )

            )

            self._horizontal_space(
                story,
                0.2
            )

            return

        for result in flagged:

            evaluation = result.get(
                "evaluation",
                {}
            )

            story.append(

                Paragraph(

                    f"<b>Response #{result.get('row_number')}</b>",

                    self.normal_style

                )

            )

            story.append(

                Paragraph(

                    f"<b>Verdict:</b> {evaluation.get('verdict','-')}",

                    self._verdict_style(
                        evaluation.get("verdict")
                    )

                )

            )

            story.append(

                Paragraph(

                    f"<b>Overall Score:</b> "
                    f"{self._score(evaluation.get('overall_score'))}",

                    self.normal_style

                )

            )

            unsupported = (
                evaluation
                .get(
                    "hallucination",
                    {}
                )
                .get(
                    "unsupported_claims",
                    []
                )
            )

            if unsupported:

                story.append(

                    Paragraph(

                        "<b>Unsupported Claims</b>",

                        self.normal_style

                    )

                )

                for claim in unsupported:

                    story.append(

                        Paragraph(

                            f"• {claim}",

                            self.small_style

                        )

                    )

            summary = evaluation.get(
                "verdict_summary"
            )

            if summary:

                story.append(

                    Paragraph(

                        "<b>Summary</b>",

                        self.normal_style

                    )

                )

                story.append(

                    Paragraph(

                        summary,

                        self.small_style

                    )

                )

            self._horizontal_space(
                story,
                0.25
            )

        story.append(
            PageBreak()
        )


    # ==========================================
    # IMPROVEMENT RECOMMENDATIONS
    # ==========================================

    def _add_recommendations(
        self,
        story,
        batch_results
    ):

        analytics = batch_results.get(
            "analytics",
            {}
        )

        self._section_title(
            story,
            "Improvement Recommendations"
        )

        recommendations = []

        weakest = analytics.get(
            "weakest_dimension"
        )

        if weakest == "Relevance":

            recommendations.append(
                "Improve response relevance by focusing more directly on the user's question."
            )

        elif weakest == "Accuracy":

            recommendations.append(
                "Improve factual correctness and verify important claims before generating responses."
            )

        elif weakest == "Hallucination":

            recommendations.append(
                "Reduce unsupported claims and improve grounding using reliable reference material."
            )

        elif weakest == "Completeness":

            recommendations.append(
                "Provide more complete answers that cover all important aspects of the question."
            )

        if analytics.get(
            "hallucination_frequency",
            0
        ) > 20:

            recommendations.append(
                "Hallucination frequency is relatively high. Increase retrieval grounding and reference verification."
            )

        average = batch_results.get(
            "average_score"
        )

        if average is not None and average < 7:

            recommendations.append(
                "Overall response quality is below the desired threshold. Review prompts and improve response generation."
            )

        if not recommendations:

            recommendations.append(
                "The evaluated responses demonstrate consistently good quality. Continue maintaining strong factual grounding and comprehensive answers."
            )

        for recommendation in recommendations:

            story.append(

                Paragraph(

                    f"• {recommendation}",

                    self.normal_style

                )

            )

        self._horizontal_space(
            story,
            0.2
        )

        story.append(

            Paragraph(

                "<b>End of Report</b>",

                self.heading_style

            )

        )

    # ==========================================
    # GENERATE PDF REPORT
    # ==========================================

    def generate_report(
        self,
        batch_results,
        output_path
    ):

        """
        Generate the complete batch evaluation report.

        Parameters
        ----------
        batch_results : dict
            Dictionary returned by BatchEvaluator.evaluate_csv()

        output_path : str
            Destination PDF path.

        Returns
        -------
        str
            Path of the generated PDF.
        """

        output_directory = os.path.dirname(output_path)

        if output_directory:

            os.makedirs(
                output_directory,
                exist_ok=True
            )

        document = SimpleDocTemplate(

            output_path,

            rightMargin=0.6 * inch,

            leftMargin=0.6 * inch,

            topMargin=0.7 * inch,

            bottomMargin=0.7 * inch

        )

        story = []

        # ----------------------------------
        # Cover Page
        # ----------------------------------

        self._add_cover_page(
            story,
            batch_results
        )

        # ----------------------------------
        # Executive Summary
        # ----------------------------------

        self._add_executive_summary(
            story,
            batch_results
        )

        # ----------------------------------
        # Batch Analytics
        # ----------------------------------

        self._add_batch_analytics(
            story,
            batch_results
        )

        # ----------------------------------
        # Verdict Distribution
        # ----------------------------------

        self._add_verdict_distribution(
            story,
            batch_results
        )

        # ----------------------------------
        # Batch Summary
        # ----------------------------------

        self._add_batch_summary(
            story,
            batch_results
        )

        # ----------------------------------
        # Individual Results
        # ----------------------------------

        self._add_individual_results(
            story,
            batch_results
        )

        # ----------------------------------
        # Flagged Responses
        # ----------------------------------

        self._add_flagged_responses(
            story,
            batch_results
        )

        # ----------------------------------
        # Recommendations
        # ----------------------------------

        self._add_recommendations(
            story,
            batch_results
        )

        # ----------------------------------
        # Footer
        # ----------------------------------

        story.append(

            Spacer(
                1,
                0.3 * inch
            )

        )

        story.append(

            Paragraph(

                "<font color='#6B7280'>"
                "<b>Generated by</b><br/>"
                "AI Response Quality Evaluator"
                "<br/>"
                "</font>",

                self.small_style

            )

        )

        document.build(
            story
        )

        return output_path