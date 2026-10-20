"""Run the six mandatory screening-assignment queries and save answers/citations."""
from config import RESULTS_PATH, OUTPUT_DIR
from rag import answer_query, format_result

QUERIES = [
    "SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष?",
    "कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?",
    "पोखरण-II में कलाम की क्या भूमिका थी?",
    "Which institution did Kalam attend to study aeronautical engineering?",
    "Who co-wrote the autobiography, and in what year was it published?",
    "How and where did Kalam die in 2015?",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sections = ["# MegaMindz Hindi PDF RAG — Six Required Queries", "", "Answers and citations are generated at run time from retrieved chunk metadata. Validate all answers against the PDF before submission.", ""]
    for i, query in enumerate(QUERIES, 1):
        print(f"\n[{i}/6] {query}")
        rendered = format_result(answer_query(query))
        print(rendered)
        sections.extend([rendered, "\n---\n"])
    RESULTS_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"\nSaved report: {RESULTS_PATH}")

if __name__ == "__main__":
    main()
