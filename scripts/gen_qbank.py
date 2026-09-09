import pathlib, json

questions = json.loads(open('scripts/_qbank_data.json', encoding='utf-8').read())

lines = [
    '"""',
    'MahaArogya - Approved Question Bank v2',
    '48 questions across all 16 symptom codes, 5 languages each.',
    'Safety Rule: AI subsystem MUST ONLY select from this approved bank.',
    '"""',
    '',
    'from ai.questions.schemas import ApprovedQuestion',
    '',
    'APPROVED_QUESTION_BANK: list[ApprovedQuestion] = [',
]

for q in questions:
    lines.append('    ApprovedQuestion(')
    for k, v in q.items():
        lines.append(f'        {k}={repr(v)},')
    lines.append('    ),')

lines += [']', '', '', 'def get_all_questions() -> list[ApprovedQuestion]:', '    return APPROVED_QUESTION_BANK', '']
pathlib.Path('ai/questions/question_bank.py').write_text('\n'.join(lines), encoding='utf-8')
print(f'Written {len(questions)} questions')
