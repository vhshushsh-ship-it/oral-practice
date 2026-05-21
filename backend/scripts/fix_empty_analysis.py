"""Fix the 2 sentences with empty connected_speech from failed LLM calls."""
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, release_db


SENTENCE_1 = "Nothing can substitute real world experience when it comes to getting started in user experience design."
SENTENCE_1_CS = [
    {
        "words": "Nothing can substitute",
        "phonetic": "/ˈnʌθɪŋ kæn ˈsʌbstɪtjuːt/",
        "description": "Nothing结尾的/ŋ/与can开头的/k/发生辅元连读；can弱读为/kæn/，结尾的/n/与substitute开头的/s/发生辅元连读",
    },
    {
        "words": "real world experience",
        "phonetic": "/rɪəl wɜːld ɪkˈspɪəriəns/",
        "description": "real结尾的/l/与world开头的/w/发生辅元连读；world结尾的/d/与experience开头的/ɪ/相邻，发生不完全爆破（失爆）",
    },
    {
        "words": "when it comes to",
        "phonetic": "/wen ɪt kʌmz tu/",
        "description": "when结尾的/n/与it开头的/ɪ/发生辅元连读；it结尾的/t/与comes开头的/k/相邻，发生不完全爆破（失爆）；comes结尾的/z/与to的/tu/发生辅音连读；to弱读为/tu/",
    },
    {
        "words": "getting started in",
        "phonetic": "/ˈɡetɪŋ ˈstɑːtɪd ɪn/",
        "description": "getting结尾的/ŋ/与started开头的/st/发生辅元连读；started结尾的/d/与in开头的/ɪ/发生辅元连读",
    },
    {
        "words": "user experience design",
        "phonetic": "/ˈjuːzə ɪkˈspɪəriəns dɪˈzaɪn/",
        "description": "user结尾的/r/与experience开头的/ɪ/发生r连读；experience结尾的/s/与design开头的/d/发生辅音连读",
    },
]
SENTENCE_1_SG_SEG = "Nothing can substitute / real world experience / when it comes to / getting started / in user experience design."
SENTENCE_1_SG_EXP = "主语+谓语/宾语/时间状语从句引导词/动名词短语/介词短语"

SENTENCE_2 = "The head teacher said he notified parents of the updated rules in an email in June."
SENTENCE_2_CS = [
    {
        "words": "The head teacher said",
        "phonetic": "/ðə hed ˈtiːtʃə sed/",
        "description": "the弱读为/ðə/，与head开头的/h/发生辅元连读（h弱读）；head结尾的/d/与teacher开头的/t/相邻，发生不完全爆破（失爆）；teacher结尾的/ə/与said开头的/s/发生辅元连读",
    },
    {
        "words": "he notified parents",
        "phonetic": "/hi ˈnəʊtɪfaɪd ˈpeərənts/",
        "description": "he结尾的/i/与notified开头的/n/发生辅元连读；notified结尾的/d/与parents开头的/p/相邻，发生不完全爆破（失爆）",
    },
    {
        "words": "of the updated rules",
        "phonetic": "/əv ðə ʌpˈdeɪtɪd ruːlz/",
        "description": "of弱读为/əv/，与the的/ðə/发生辅元连读；the弱读为/ðə/，与updated开头的/ʌ/发生元元连读；updated结尾的/d/与rules开头的/r/发生辅元连读",
    },
    {
        "words": "in an email in June",
        "phonetic": "/ɪn ən ˈiːmeɪl ɪn dʒuːn/",
        "description": "in结尾的/n/与an的/ən/发生辅元连读；an结尾的/n/与email开头的/iː/发生辅元连读；email结尾的/l/与in开头的/ɪ/发生辅元连读；in结尾的/n/与June开头的/dʒ/发生辅元连读",
    },
]
SENTENCE_2_SG_SEG = "The head teacher said / he notified parents / of the updated rules / in an email / in June."
SENTENCE_2_SG_EXP = "主语+谓语/宾语从句/定语/方式状语/时间状语"


async def main():
    db = await get_db()
    try:
        async with db.cursor() as cur:
            for text, cs, sg_seg, sg_exp in [
                (SENTENCE_1, SENTENCE_1_CS, SENTENCE_1_SG_SEG, SENTENCE_1_SG_EXP),
                (SENTENCE_2, SENTENCE_2_CS, SENTENCE_2_SG_SEG, SENTENCE_2_SG_EXP),
            ]:
                cs_json = json.dumps(cs, ensure_ascii=False)
                await cur.execute(
                    "UPDATE listening_sentence_analysis SET connected_speech = %s, sense_groups_segmented = %s, sense_groups_explanation = %s WHERE sentence_text = %s",
                    (cs_json, sg_seg, sg_exp, text),
                )
                print(f"Updated: {text[:60]}...")
            await db.commit()
            print("Done.")
    finally:
        await release_db(db)


if __name__ == "__main__":
    asyncio.run(main())
