"""Regenerate ALL sentence analysis data and import to MySQL."""
import json
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db, release_db

# ============================================================
# All sentence analysis data: { sentence_text: { connected_speech, sense_groups } }
# ============================================================

DATA: dict[str, dict] = {}

# ─── cet4-2025-12 Section A: News Reports ───

DATA["A terrified cat has survived a five-mile round trip under the engine cover of a car on a school run."] = {
    "connected_speech": [
        {"words": "A terrified cat", "phonetic": "/ə ˈterɪfaɪd kæt/", "description": "A弱读为/ə/，与terrified开头的/t/发生辅元连读；terrified结尾的/d/与cat开头的/k/相邻，发生不完全爆破（失爆），/d/仅保留口型不送气。"},
        {"words": "has survived", "phonetic": "/həz səˈvaɪvd/", "description": "has弱读为/həz/，结尾的/z/与survived开头的/s/相邻，发生辅音连读，可轻微延长避免吞音。"},
        {"words": "a five-mile round trip", "phonetic": "/ə ˈfaɪvmaɪl raʊnd trɪp/", "description": "a弱读为/ə/，与five开头的/f/发生辅元连读；five结尾的/v/与mile开头的/m/发生辅音连读；round结尾的/d/与trip开头的/t/相邻，发生不完全爆破（失爆）。"},
        {"words": "under the engine", "phonetic": "/ˈʌndər ðə ˈendʒɪn/", "description": "under结尾的/r/与the开头的/ð/发生辅音连读；the弱读为/ðə/，与engine开头的/e/发生元元连读（口语中the可弱读为/ði/更顺畅）。"},
        {"words": "cover of a car", "phonetic": "/ˈkʌvər əv ə kɑr/", "description": "cover结尾的/r/与of开头的/ə/发生r连读（辅元连读）；of弱读为/əv/，结尾的/v/与a的/ə/发生辅元连读；a的/ə/与car开头的/k/发生辅元连读。"},
        {"words": "on a school run", "phonetic": "/ɑn ə skul rʌn/", "description": "on结尾的/n/与a的/ə/发生辅元连读；a的/ə/与school开头的/s/发生辅元连读；school结尾的/l/与run开头的/r/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "A terrified cat / has survived / a five-mile round trip / under the engine cover / of a car / on a school run.",
        "explanation": "主语(A terrified cat)/谓语(has survived)/宾语核心(a five-mile round trip)/地点状语1(under the engine cover)/后置定语(of a car)/地点状语2(on a school run)，每个意群对应一个语义单元，英语母语者在每个“/”处有短暂停顿。",
    },
}

DATA["The black cat was found curled up under the engine cover of David King's car when he decided to do an oil check after dropping his grandson off at school."] = {
    "connected_speech": [
        {"words": "The black cat", "phonetic": "/ðə blæk kæt/", "description": "the弱读为/ðə/，与black开头的/b/发生辅元连读；black结尾的/k/与cat开头的/k/相邻，发生不完全爆破（失爆），前一个/k/仅保留口型。"},
        {"words": "was found curled up", "phonetic": "/wəz faʊnd kɜrld ʌp/", "description": "was弱读为/wəz/，结尾的/z/与found开头的/f/发生辅音连读；found结尾的/d/与curled开头的/k/相邻，发生不完全爆破；curled结尾的/d/与up开头的/ʌ/发生辅元连读。"},
        {"words": "under the engine cover", "phonetic": "/ˈʌndər ði ˈendʒɪn ˈkʌvər/", "description": "under结尾的/r/与the开头的/ð/发生辅音连读；the弱读为/ði/，与engine开头的/e/发生元元连读；engine结尾的/n/与cover开头的/k/发生辅元连读。"},
        {"words": "of David King's car", "phonetic": "/əv ˈdeɪvɪd kɪŋz kɑr/", "description": "of弱读为/əv/，结尾的/v/与David开头的/d/发生辅音连读；David结尾的/d/与King's开头的/k/相邻，发生不完全爆破；King's结尾的/z/与car开头的/k/发生辅音连读。"},
        {"words": "when he decided to", "phonetic": "/wen hi dɪˈsaɪdɪd tu/", "description": "when结尾的/n/与he开头的/h/发生辅元连读（h弱读时可省略）；he结尾的/i/与decided开头的/d/发生辅元连读；decided结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tu/。"},
        {"words": "do an oil check", "phonetic": "/du ən ɔɪl tʃek/", "description": "do结尾的/u/与an开头的/ə/发生元元连读（加/w/过渡音）；an结尾的/n/与oil开头的/ɔɪ/发生辅元连读；oil结尾的/l/与check开头的/tʃ/发生辅音连读。"},
        {"words": "after dropping his grandson off at school", "phonetic": "/ˈæftər ˈdrɑpɪŋ hɪz ˈɡrænsʌn ɑf ət skul/", "description": "after结尾的/r/与dropping开头的/d/发生辅元连读（r连读）；dropping结尾的/ŋ/与his开头的/h/发生辅元连读；his结尾的/z/与grandson开头的/ɡ/发生辅音连读；off结尾的/f/与at开头的/ə/发生辅元连读；at弱读为/ət/，与school开头的/s/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The black cat was found / curled up / under the engine cover / of David King's car / when he decided to do an oil check / after dropping his grandson off at school.",
        "explanation": "主句主语+谓语(The black cat was found)/主语补足语(curled up)/地点状语(under the engine cover)/后置定语(of David King's car)/时间状语从句(when he decided to do an oil check)/时间状语从句修饰语(after dropping his grandson off at school)，意群划分遵循主语-谓语-补语-修饰语的逻辑层次。",
    },
}

DATA["We weren't even sure it was alive, so I gently pushed it with a stick to check it was breathing and saw it was a terrified little cat."] = {
    "connected_speech": [
        {"words": "We weren't even sure", "phonetic": "/wi wɜrnt ˈivən ʃʊr/", "description": "weren't结尾的/t/与even开头的/i/发生辅元连读；even结尾的/n/与sure开头的/ʃ/发生辅元连读；sure结尾的/r/在英式发音中不发音，在美式中可与后续元音发生r连读。"},
        {"words": "it was alive", "phonetic": "/ɪt wəz əˈlaɪv/", "description": "it结尾的/t/与was开头的/w/相邻，发生不完全爆破（失爆）；was弱读为/wəz/，结尾的/z/与alive开头的/ə/发生辅元连读。"},
        {"words": "pushed it with a stick", "phonetic": "/pʊʃt ɪt wɪð ə stɪk/", "description": "pushed结尾的/t/与it开头的/ɪ/发生辅元连读；it结尾的/t/与with开头的/w/相邻，发生不完全爆破；with结尾的/ð/与a的/ə/发生辅元连读；a的/ə/与stick开头的/s/发生辅元连读。"},
        {"words": "to check it was breathing", "phonetic": "/tə tʃek ɪt wəz ˈbriðɪŋ/", "description": "to弱读为/tə/，与check开头的/tʃ/发生辅元连读；check结尾的/k/与it开头的/ɪ/发生辅元连读；it结尾的/t/与was开头的/w/相邻，发生不完全爆破；was弱读为/wəz/。"},
        {"words": "and saw it was", "phonetic": "/ən sɔ ɪt wəz/", "description": "and弱读为/ən/，结尾的/d/省略，/n/与saw开头的/s/发生辅元连读；saw结尾的元音/ɔ/与it开头的/ɪ/发生元元连读；it结尾的/t/与was开头的/w/相邻，发生不完全爆破。"},
        {"words": "a terrified little cat", "phonetic": "/ə ˈterɪfaɪd ˈlɪtəl kæt/", "description": "a弱读为/ə/，与terrified开头的/t/发生辅元连读；terrified结尾的/d/与little开头的/l/发生辅音连读；little结尾的/l/与cat开头的/k/发生辅音连读（dark l过渡）。"},
    ],
    "sense_groups": {
        "segmented": "We weren't even sure it was alive, / so I gently pushed it / with a stick / to check it was breathing / and saw / it was a terrified little cat.",
        "explanation": "第一个分句(We weren't even sure it was alive)/结果连接词+第二分句主语谓语(so I gently pushed it)/方式状语(with a stick)/目的状语(to check it was breathing)/并列谓语(and saw)/宾语从句(it was a terrified little cat)，意群按分句和功能成分划分，逗号处为自然停顿点。",
    },
}

DATA["Following a rescue by UK charity Cats Protection, the four year old cat was later reunited with its owner, Mr King's neighbour."] = {
    "connected_speech": [
        {"words": "Following a rescue", "phonetic": "/ˈfɑloʊɪŋ ə ˈreskju/", "description": "Following结尾的/ŋ/与a的/ə/发生辅元连读；a的/ə/与rescue开头的/r/发生辅元连读。"},
        {"words": "by UK charity", "phonetic": "/baɪ juˈkeɪ ˈtʃærɪti/", "description": "by结尾的/aɪ/与UK开头的/juː/发生元元连读（加/j/过渡音）；UK结尾的/eɪ/与charity开头的/tʃ/发生元辅连读。"},
        {"words": "Cats Protection", "phonetic": "/kæts prəˈtekʃən/", "description": "Cats结尾的/s/与Protection开头的/p/发生辅音连读，/s/可略微延长。"},
        {"words": "the four year old cat", "phonetic": "/ðə fɔr jɪr oʊld kæt/", "description": "the弱读为/ðə/，与four开头的/f/发生辅元连读；four结尾的/r/与year开头的/j/发生r连读；year结尾的/r/与old开头的/oʊ/发生r连读；old结尾的/d/与cat开头的/k/相邻，发生不完全爆破。"},
        {"words": "was later reunited", "phonetic": "/wəz ˈleɪtər ˌrijuˈnaɪtɪd/", "description": "was弱读为/wəz/，结尾的/z/与later开头的/l/发生辅元连读；later结尾的/r/与reunited开头的/r/发生辅音连读，可合并或轻微延长。"},
        {"words": "with its owner", "phonetic": "/wɪð ɪts ˈoʊnər/", "description": "with结尾的/ð/与its开头的/ɪ/发生辅元连读；its结尾的/s/与owner开头的/oʊ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Following a rescue / by UK charity Cats Protection, / the four year old cat / was later reunited / with its owner, / Mr King's neighbour.",
        "explanation": "状语短语(Following a rescue)/状语修饰语(by UK charity Cats Protection)/主语(the four year old cat)/谓语(was later reunited)/介词短语(with its owner)/同位语(Mr King's neighbour)，逗号分隔处为自然停顿，每个意群表达一个完整的语义片段。",
    },
}

DATA["In less than a month, the Special Olympics Spring Games will make a return to Fayetteville for the first time in five years."] = {
    "connected_speech": [
        {"words": "In less than a month", "phonetic": "/ɪn les ðən ə mʌnθ/", "description": "in结尾的/n/与less开头的/l/发生辅元连读；less结尾的/s/与than开头的/ð/发生辅音连读；than弱读为/ðən/，结尾的/n/与a的/ə/发生辅元连读。"},
        {"words": "the Special Olympics Spring Games", "phonetic": "/ðə ˈspeʃəl əˈlɪmpɪks sprɪŋ ɡeɪmz/", "description": "the弱读为/ðə/，与Special开头的/s/发生辅元连读；Special结尾的/l/与Olympics开头的/ə/发生辅元连读；Olympics结尾的/s/与Spring开头的/s/相邻，可合并延长；Spring结尾的/ŋ/与Games开头的/ɡ/发生辅元连读。"},
        {"words": "will make a return", "phonetic": "/wɪl meɪk ə rɪˈtɜrn/", "description": "will结尾的/l/与make开头的/m/发生辅音连读；make结尾的/k/与a的/ə/发生辅元连读；a的/ə/与return开头的/r/发生辅元连读。"},
        {"words": "to Fayetteville", "phonetic": "/tə ˈfeɪɛtvɪl/", "description": "to弱读为/tə/，与Fayetteville开头的/f/发生辅元连读。"},
        {"words": "for the first time in five years", "phonetic": "/fər ðə fɜrst taɪm ɪn faɪv jɪrz/", "description": "for弱读为/fər/，结尾的/r/与the开头的/ð/发生辅音连读；the弱读为/ðə/；first结尾的/t/与time开头的/t/相邻，发生不完全爆破；time结尾的/m/与in开头的/ɪ/发生辅元连读；five结尾的/v/与years开头的/j/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "In less than a month, / the Special Olympics Spring Games / will make a return / to Fayetteville / for the first time / in five years.",
        "explanation": "时间状语(In less than a month)/主语(the Special Olympics Spring Games)/谓语+宾语(will make a return)/地点状语(to Fayetteville)/时间状语(for the first time)/时间状语修饰语(in five years)，按语义单元划分，状语和主谓宾各自独立成意群。",
    },
}

DATA["Event organizer Benjamin Koalzick says he's excited that athletes will get a chance to come back and demonstrate their abilities."] = {
    "connected_speech": [
        {"words": "Event organizer", "phonetic": "/ɪˈvent ˈɔɡənaɪzər/", "description": "Event结尾的/t/与organizer开头的/ɔ/发生辅元连读。"},
        {"words": "Benjamin Koalzick says", "phonetic": "/ˈbendʒəmɪn ˈkoʊlzɪk sez/", "description": "Benjamin结尾的/n/与Koalzick开头的/k/发生辅元连读；Koalzick结尾的/k/与says开头的/s/发生辅音连读。"},
        {"words": "he's excited that", "phonetic": "/hiz ɪkˈsaɪtɪd ðət/", "description": "he's结尾的/z/与excited开头的/ɪ/发生辅元连读；excited结尾的/d/与that开头的/ð/相邻，发生不完全爆破（失爆）；that弱读为/ðət/。"},
        {"words": "athletes will get a chance", "phonetic": "/ˈæθlits wɪl ɡet ə tʃæns/", "description": "athletes结尾的/s/与will开头的/w/发生辅音连读；will结尾的/l/与get开头的/ɡ/发生辅音连读；get结尾的/t/与a的/ə/发生辅元连读；a的/ə/与chance开头的/tʃ/发生辅元连读。"},
        {"words": "to come back and", "phonetic": "/tə kʌm bæk ən/", "description": "to弱读为/tə/，与come开头的/k/发生辅元连读；come结尾的/m/与back开头的/b/发生辅音连读；back结尾的/k/与and开头的/æ/发生辅元连读；and弱读为/ən/。"},
        {"words": "demonstrate their abilities", "phonetic": "/ˈdemənstreɪt ðer əˈbɪlɪtiz/", "description": "demonstrate结尾的/t/与their开头的/ð/相邻，发生不完全爆破；their结尾的/r/与abilities开头的/ə/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "Event organizer Benjamin Koalzick says / he's excited / that athletes will get a chance / to come back / and demonstrate their abilities.",
        "explanation": "主句主语+谓语(Event organizer Benjamin Koalzick says)/宾语从句主语+谓语(he's excited)/宾语从句(that athletes will get a chance)/目的状语(to come back)/并列目的(and demonstrate their abilities)，按从句层次划分意群。",
    },
}

DATA["Organizers expect about one hundred athletes will come out to compete in a variety of events including running, throwing, and jumping."] = {
    "connected_speech": [
        {"words": "Organizers expect about", "phonetic": "/ˈɔɡənaɪzərz ɪkˈspekt əˈbaʊt/", "description": "Organizers结尾的/z/与expect开头的/ɪ/发生辅元连读；expect结尾的/t/与about开头的/ə/发生辅元连读；about弱读为/əˈbaʊt/。"},
        {"words": "one hundred athletes", "phonetic": "/wʌn ˈhʌndrəd ˈæθlits/", "description": "one结尾的/n/与hundred开头的/h/发生辅元连读（h可弱读）；hundred结尾的/d/与athletes开头的/æ/发生辅元连读。"},
        {"words": "will come out", "phonetic": "/wɪl kʌm aʊt/", "description": "will结尾的/l/与come开头的/k/发生辅音连读；come结尾的/m/与out开头的/aʊ/发生辅元连读。"},
        {"words": "to compete in a variety of events", "phonetic": "/tə kəmˈpit ɪn ə vəˈraɪrti əv ɪˈvents/", "description": "to弱读为/tə/，与compete开头的/k/发生辅元连读；compete结尾的/t/与in开头的/ɪ/发生辅元连读；in结尾的/n/与a的/ə/发生辅元连读；variety结尾的/i/与of开头的/ə/发生元元连读；of弱读为/əv/，结尾的/v/与events开头的/ɪ/发生辅元连读。"},
        {"words": "including running, throwing, and jumping", "phonetic": "/ɪnˈkludɪŋ ˈrʌnɪŋ ˈθroʊɪŋ ən ˈdʒʌmpɪŋ/", "description": "including结尾的/ŋ/与running开头的/r/发生辅元连读；running结尾的/ŋ/与throwing开头的/θ/发生辅元连读；throwing结尾的/ŋ/与and的/ən/发生辅元连读；and弱读为/ən/，结尾的/n/与jumping开头的/dʒ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Organizers expect / about one hundred athletes will come out / to compete / in a variety of events / including running, throwing, and jumping.",
        "explanation": "主句主语+谓语(Organizers expect)/宾语从句(about one hundred athletes will come out)/目的状语(to compete)/范围状语(in a variety of events)/列举说明(including running, throwing, and jumping)，按主从关系和功能成分划分意群。",
    },
}

DATA["Kawalski said it's rewarding to see athletes with special needs triumph in the games."] = {
    "connected_speech": [
        {"words": "Kawalski said it's", "phonetic": "/ˈkoʊlzɪk sed ɪts/", "description": "Kawalski结尾的/i/与said开头的/s/发生辅元连读；said结尾的/d/与it's开头的/ɪ/发生辅元连读；it's结尾的/s/与后续rewarding开头的/r/发生辅音连读。"},
        {"words": "rewarding to see", "phonetic": "/rɪˈwɔdɪŋ tə si/", "description": "rewarding结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/，结尾的/ə/与see开头的/s/发生辅元连读。"},
        {"words": "athletes with special needs", "phonetic": "/ˈæθlits wɪð ˈspeʃəl nidz/", "description": "athletes结尾的/s/与with开头的/w/发生辅音连读；with结尾的/ð/与special开头的/s/发生辅音连读；special结尾的/l/与needs开头的/n/发生辅音连读。"},
        {"words": "triumph in the games", "phonetic": "/ˈtraɪrmf ɪn ðə ɡeɪmz/", "description": "triumph结尾的/f/与in开头的/ɪ/发生辅元连读；in结尾的/n/与the的/ðə/发生辅元连读；the弱读为/ðə/，与games开头的/ɡ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Kawalski said / it's rewarding / to see athletes / with special needs / triumph in the games.",
        "explanation": "主句(Kawalski said)/宾语从句主语+谓语(it's rewarding)/不定式短语(to see athletes)/后置定语(with special needs)/不定式的宾语补足语(triumph in the games)，按语义层次划分，每个意群承载一个核心信息。",
    },
}

DATA["A German supermarket has been ordered to destroy its chocolate rabbits after losing a court battle with a Swiss chocolate manufacturer."] = {
    "connected_speech": [
        {"words": "A German supermarket", "phonetic": "/ə ˈdʒɜrmən ˈsupəmɑkɪt/", "description": "A弱读为/ə/，与German开头的/dʒ/发生辅元连读；German结尾的/n/与supermarket开头的/s/发生辅元连读。"},
        {"words": "has been ordered to", "phonetic": "/həz bin ˈɔdəd tə/", "description": "has弱读为/həz/，结尾的/z/与been开头的/b/发生辅音连读；been结尾的/n/与ordered开头的/ɔ/发生辅元连读；ordered结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "destroy its chocolate rabbits", "phonetic": "/dɪˈstrɔɪ ɪts ˈtʃɑklət ˈræbɪts/", "description": "destroy结尾的/ɔɪ/与its开头的/ɪ/发生元元连读；its结尾的/s/与chocolate开头的/tʃ/发生辅音连读；chocolate结尾的/t/与rabbits开头的/r/发生辅元连读。"},
        {"words": "after losing a court battle", "phonetic": "/ˈæftər ˈluzɪŋ ə kɔt ˈbætəl/", "description": "after结尾的/r/与losing开头的/l/发生辅元连读(r连读)；losing结尾的/ŋ/与a的/ə/发生辅元连读；court结尾的/t/与battle开头的/b/相邻，发生不完全爆破（失爆）。"},
        {"words": "with a Swiss chocolate manufacturer", "phonetic": "/wɪð ə swɪs ˈtʃɑklət ˌmænjuˈfæktʃərər/", "description": "with结尾的/ð/与a的/ə/发生辅元连读；a的/ə/与Swiss开头的/s/发生辅元连读；Swiss结尾的/s/与chocolate开头的/tʃ/发生辅音连读；chocolate结尾的/t/与manufacturer开头的/m/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "A German supermarket / has been ordered / to destroy its chocolate rabbits / after losing a court battle / with a Swiss chocolate manufacturer.",
        "explanation": "主语(A German supermarket)/谓语(has been ordered)/主语补足语(to destroy its chocolate rabbits)/时间状语(after losing a court battle)/状语修饰语(with a Swiss chocolate manufacturer)，意群按主-谓-补-状的结构层次划分。",
    },
}

DATA["The Swiss firm had argued its gold wrapped chocolate rabbit deserved copyright protection from a similar product sold by the budget supermarket."] = {
    "connected_speech": [
        {"words": "The Swiss firm had argued", "phonetic": "/ðə swɪs fɜrm həd ˈɑɡjud/", "description": "the弱读为/ðə/，与Swiss开头的/s/发生辅元连读；Swiss结尾的/s/与firm开头的/f/发生辅音连读；had弱读为/həd/，结尾的/d/与argued开头的/ɑ/发生辅元连读。"},
        {"words": "its gold wrapped chocolate rabbit", "phonetic": "/ɪts ɡoʊld ræpt ˈtʃɑklət ˈræbɪt/", "description": "its结尾的/s/与gold开头的/ɡ/发生辅音连读；gold结尾的/d/与wrapped开头的/r/发生辅元连读；wrapped结尾的/t/与chocolate开头的/tʃ/相邻，发生不完全爆破；chocolate结尾的/t/与rabbit开头的/r/发生辅元连读。"},
        {"words": "deserved copyright protection", "phonetic": "/dɪˈzɜrvd ˈkɑpiraɪt prəˈtekʃən/", "description": "deserved结尾的/d/与copyright开头的/k/相邻，发生不完全爆破（失爆）；copyright结尾的/t/与protection开头的/p/相邻，发生不完全爆破。"},
        {"words": "from a similar product", "phonetic": "/frəm ə ˈsɪmɪlər ˈprɑdʌkt/", "description": "from弱读为/frəm/，结尾的/m/与a的/ə/发生辅元连读；similar结尾的/r/与product开头的/p/发生辅元连读（r连读）。"},
        {"words": "sold by the budget supermarket", "phonetic": "/soʊld baɪ ðə ˈbʌdʒɪt ˈsupəmɑkɪt/", "description": "sold结尾的/d/与by开头的/b/相邻，发生不完全爆破；by结尾的/aɪ/与the的/ðə/发生元元连读；budget结尾的/t/与supermarket开头的/s/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "The Swiss firm had argued / its gold wrapped chocolate rabbit / deserved copyright protection / from a similar product / sold by the budget supermarket.",
        "explanation": "主句(The Swiss firm had argued)/宾语从句主语(its gold wrapped chocolate rabbit)/宾语从句谓语+宾语(deserved copyright protection)/来源状语(from a similar product)/后置定语(sold by the budget supermarket)，按从句层次和修饰关系划分。"},
}

DATA["Switzerland's highest court agreed and overturned a ruling last year that had sided with the supermarket."] = {
    "connected_speech": [
        {"words": "Switzerland's highest court", "phonetic": "/ˈswɪtsələndz ˈhaɪɪst kɔt/", "description": "Switzerland's结尾的/z/与highest开头的/h/发生辅元连读；highest结尾的/t/与court开头的/k/相邻，发生不完全爆破（失爆）。"},
        {"words": "agreed and overturned", "phonetic": "/əˈɡrid ən ˌoʊvəˈtɜrnd/", "description": "agreed结尾的/d/与and开头的/æ/发生辅元连读；and弱读为/ən/，结尾的/n/与overturned开头的/oʊ/发生辅元连读。"},
        {"words": "a ruling last year", "phonetic": "/ə ˈrulɪŋ læst jɪr/", "description": "a弱读为/ə/，与ruling开头的/r/发生辅元连读；ruling结尾的/ŋ/与last开头的/l/发生辅元连读；last结尾的/t/与year开头的/j/相邻，发生不完全爆破。"},
        {"words": "that had sided with", "phonetic": "/ðət həd ˈsaɪdɪd wɪð/", "description": "that弱读为/ðət/，与had开头的/h/发生辅元连读；had弱读为/həd/，结尾的/d/与sided开头的/s/相邻，发生不完全爆破；sided结尾的/d/与with开头的/w/相邻，发生不完全爆破。"},
        {"words": "the supermarket", "phonetic": "/ðə ˈsupəmɑkɪt/", "description": "the弱读为/ðə/，与supermarket开头的/s/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Switzerland's highest court / agreed / and overturned / a ruling last year / that had sided with the supermarket.",
        "explanation": "主语(Switzerland's highest court)/谓语1(agreed)/并列连词+谓语2(and overturned)/宾语(a ruling last year)/定语从句(that had sided with the supermarket)，谓语并列结构分属不同意群以突出动作的递进关系。",
    },
}

DATA["The court suggested the chocolate needn't be wasted; it could be melted for use in other products."] = {
    "connected_speech": [
        {"words": "The court suggested", "phonetic": "/ðə kɔt səˈdʒestɪd/", "description": "the弱读为/ðə/，与court开头的/k/发生辅元连读；court结尾的/t/与suggested开头的/s/相邻，发生不完全爆破。"},
        {"words": "the chocolate needn't be wasted", "phonetic": "/ðə ˈtʃɑklət ˈnidnt bi ˈweɪstɪd/", "description": "the弱读为/ðə/，与chocolate开头的/tʃ/发生辅元连读；chocolate结尾的/t/与needn't开头的/n/相邻，发生不完全爆破；needn't结尾的/t/与be开头的/b/相邻，发生不完全爆破。"},
        {"words": "it could be melted", "phonetic": "/ɪt kʊd bi ˈmeltɪd/", "description": "it结尾的/t/与could开头的/k/相邻，发生不完全爆破（失爆）；could结尾的/d/与be开头的/b/相邻，发生不完全爆破。"},
        {"words": "for use in other products", "phonetic": "/fər juz ɪn ˈʌðər ˈprɑdʌkts/", "description": "for弱读为/fər/，结尾的/r/与use开头的/j/发生r连读；use结尾的/z/与in开头的/ɪ/发生辅元连读；in结尾的/n/与other开头的/ʌ/发生辅元连读；other结尾的/r/与products开头的/p/发生辅元连读（r连读）。"},
    ],
    "sense_groups": {
        "segmented": "The court suggested / the chocolate needn't be wasted; / it could be melted / for use / in other products.",
        "explanation": "主句(The court suggested)/宾语从句1(the chocolate needn't be wasted)/宾语从句2(it could be melted)/目的状语(for use)/范围状语(in other products)，分号处为最大停顿，各意群按语义完整性划分。",
    },
}

DATA["The Swiss manufacturer's rabbit has a red bow and bell, while the German supermarket's has a green bow and bell."] = {
    "connected_speech": [
        {"words": "The Swiss manufacturer's rabbit", "phonetic": "/ðə swɪs ˌmænjuˈfæktʃərərz ˈræbɪt/", "description": "Swiss结尾的/s/与manufacturer's开头的/m/发生辅音连读；manufacturer's结尾的/z/与rabbit开头的/r/发生辅音连读。"},
        {"words": "has a red bow and bell", "phonetic": "/həz ə red boʊ ən bel/", "description": "has弱读为/həz/，结尾的/z/与a的/ə/发生辅元连读；red结尾的/d/与bow开头的/b/相邻，发生不完全爆破；bow结尾的/oʊ/与and的/ən/发生元元连读；and弱读为/ən/。"},
        {"words": "while the German supermarket's", "phonetic": "/waɪl ðə ˈdʒɜrmən ˈsupəmɑkɪts/", "description": "while结尾的/l/与the的/ðə/发生辅音连读；German结尾的/n/与supermarket's开头的/s/发生辅元连读。"},
        {"words": "has a green bow and bell", "phonetic": "/həz ə ɡrin boʊ ən bel/", "description": "has弱读为/həz/，结尾的/z/与a的/ə/发生辅元连读；green结尾的/n/与bow开头的/b/发生辅元连读；bow结尾的/oʊ/与and的/ən/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "The Swiss manufacturer's rabbit / has a red bow and bell, / while the German supermarket's / has a green bow and bell.",
        "explanation": "主语1(The Swiss manufacturer's rabbit)/谓语+宾语1(has a red bow and bell)/对比连词+主语2(while the German supermarket's)/谓语+宾语2(has a green bow and bell)，按对比结构的两个分句各分两组意群，逗号为自然停顿。",
    },
}

# ─── cet4-2025-12 Section B: Long Conversations ───

DATA["Can you please hand me that book over there? It has instructions for making a winter bean salad."] = {
    "connected_speech": [
        {"words": "Can you please", "phonetic": "/kən ju pliz/", "description": "can弱读为/kən/；can结尾的/n/与you开头的/j/发生辅元连读；you结尾的/u/与please开头的/p/发生辅元连读。"},
        {"words": "hand me that book", "phonetic": "/hænd mi ðət bʊk/", "description": "hand结尾的/d/与me开头的/m/相邻，发生不完全爆破（失爆）；that弱读为/ðət/，结尾的/t/与book开头的/b/相邻，发生不完全爆破。"},
        {"words": "over there", "phonetic": "/ˈoʊvər ðer/", "description": "over结尾的/r/与there开头的/ð/发生辅音连读（r连读）。"},
        {"words": "It has instructions", "phonetic": "/ɪt həz ɪnˈstrʌkʃənz/", "description": "it结尾的/t/与has开头的/h/相邻，发生不完全爆破；has弱读为/həz/，结尾的/z/与instructions开头的/ɪ/发生辅元连读。"},
        {"words": "for making a", "phonetic": "/fər ˈmeɪkɪŋ ə/", "description": "for弱读为/fər/，结尾的/r/与making开头的/m/发生辅元连读(r连读)；making结尾的/ŋ/与a的/ə/发生辅元连读。"},
        {"words": "winter bean salad", "phonetic": "/ˈwɪntər bin ˈsæləd/", "description": "winter结尾的/r/与bean开头的/b/发生辅元连读(r连读)；bean结尾的/n/与salad开头的/s/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Can you please / hand me that book over there? / It has instructions / for making / a winter bean salad.",
        "explanation": "礼貌请求(Can you please)/核心动作+宾语+地点(hand me that book over there)/第二句主语+谓语(It has instructions)/目的状语(for making)/宾语(a winter bean salad)，两句之间为句号大停顿，各意群按句子成分划分。",
    },
}

DATA["My sister's boyfriend is coming over for dinner. He's vegetarian, so I need to make a lot of vegetable dishes."] = {
    "connected_speech": [
        {"words": "My sister's boyfriend", "phonetic": "/maɪ ˈsɪstərz ˈbɔɪfrend/", "description": "sister's结尾的/z/与boyfriend开头的/b/发生辅音连读。"},
        {"words": "is coming over for dinner", "phonetic": "/ɪz ˈkʌmɪŋ ˈoʊvər fər ˈdɪnər/", "description": "is结尾的/z/与coming开头的/k/发生辅音连读；coming结尾的/ŋ/与over开头的/oʊ/发生辅元连读；over结尾的/r/与for开头的/f/发生辅元连读(r连读)；for弱读为/fər/。"},
        {"words": "He's vegetarian", "phonetic": "/hiz ˌvedʒɪˈteriən/", "description": "He's结尾的/z/与vegetarian开头的/v/发生辅音连读。"},
        {"words": "so I need to make", "phonetic": "/soʊ aɪ nid tə meɪk/", "description": "so结尾的/oʊ/与I开头的/aɪ/发生元元连读；need结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "a lot of vegetable dishes", "phonetic": "/ə lɑt əv ˈvedʒtəbəl ˈdɪʃɪz/", "description": "lot结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与vegetable开头的/v/可合并或轻微延长；vegetable结尾的/l/与dishes开头的/d/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "My sister's boyfriend / is coming over / for dinner. / He's vegetarian, / so I need to make / a lot of vegetable dishes.",
        "explanation": "主语(My sister's boyfriend)/谓语+状语(is coming over)/目的状语(for dinner)/第二句主语+谓语(He's vegetarian)/结果状语(so I need to make)/宾语(a lot of vegetable dishes)，句号处为大停顿，各意群按信息焦点分组。",
    },
}

DATA["He only eats vegetables, no meat. That doesn't sound like a very balanced diet."] = {
    "connected_speech": [
        {"words": "He only eats vegetables", "phonetic": "/hi ˈoʊnli its ˈvedʒtəbəlz/", "description": "only结尾的/i/与eats开头的/i/发生元元连读；eats结尾的/s/与vegetables开头的/v/发生辅音连读。"},
        {"words": "no meat", "phonetic": "/noʊ mit/", "description": "no结尾的/oʊ/与meat开头的/m/发生辅元连读。"},
        {"words": "That doesn't sound like", "phonetic": "/ðət ˈdʌznt saʊnd laɪk/", "description": "that弱读为/ðət/；doesn't结尾的/t/与sound开头的/s/相邻，发生不完全爆破（失爆）；sound结尾的/d/与like开头的/l/相邻，发生不完全爆破。"},
        {"words": "a very balanced diet", "phonetic": "/ə ˈveri ˈbælənst ˈdaɪrt/", "description": "a弱读为/ə/，与very开头的/v/发生辅元连读；balanced结尾的/t/与diet开头的/d/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "He only eats vegetables, / no meat. / That doesn't sound like / a very balanced diet.",
        "explanation": "第一句谓语+宾语(He only eats vegetables)/同位补充(no meat)/第二句主语+谓语(That doesn't sound like)/表语(a very balanced diet)，按句子分界和核心成分划分意群。",
    },
}

DATA["How can he get enough protein? What does he do to strengthen his muscles and all that?"] = {
    "connected_speech": [
        {"words": "How can he get", "phonetic": "/haʊ kən hi ɡet/", "description": "can弱读为/kən/；can结尾的/n/与he开头的/h/发生辅元连读（h可弱读省略）；he结尾的/i/与get开头的/ɡ/发生辅元连读。"},
        {"words": "enough protein", "phonetic": "/ɪˈnʌf ˈproʊtin/", "description": "enough结尾的/f/与protein开头的/p/发生辅音连读。"},
        {"words": "What does he do", "phonetic": "/wɑt dəz hi du/", "description": "what结尾的/t/与does开头的/d/相邻，发生不完全爆破；does弱读为/dəz/，结尾的/z/与he开头的/h/发生辅元连读；he结尾的/i/与do开头的/d/发生辅元连读。"},
        {"words": "to strengthen his muscles", "phonetic": "/tə ˈstreŋθən hɪz ˈmʌsəlz/", "description": "to弱读为/tə/，与strengthen开头的/s/发生辅元连读；strengthen结尾的/n/与his开头的/h/发生辅元连读；his结尾的/z/与muscles开头的/m/发生辅音连读。"},
        {"words": "and all that", "phonetic": "/ən ɔl ðət/", "description": "and弱读为/ən/，结尾的/n/与all开头的/ɔ/发生辅元连读；all结尾的/l/与that的/ðət/发生辅音连读；that弱读为/ðət/。"},
    ],
    "sense_groups": {
        "segmented": "How can he get / enough protein? / What does he do / to strengthen his muscles / and all that?",
        "explanation": "疑问词+助动词+主语+谓语(How can he get)/宾语(enough protein)/第二句疑问词+助动词+主语+谓语(What does he do)/目的状语(to strengthen his muscles)/补充语(and all that)，按两个疑问句及其内部成分划分。",
    },
}

DATA["Apparently that's no problem. He eats a variety of different vegetables and nuts, especially those with high amounts of protein."] = {
    "connected_speech": [
        {"words": "Apparently that's no problem", "phonetic": "/əˈpærəntli ðəts noʊ ˈprɑbləm/", "description": "Apparently结尾的/i/与that's开头的/ð/发生辅元连读；that's结尾的/s/与no开头的/n/发生辅音连读。"},
        {"words": "He eats a variety of", "phonetic": "/hi its ə vəˈraɪrti əv/", "description": "eats结尾的/s/与a的/ə/发生辅元连读；a的/ə/与variety开头的/v/发生辅元连读；variety结尾的/i/与of开头的/ə/发生元元连读；of弱读为/əv/。"},
        {"words": "different vegetables and nuts", "phonetic": "/ˈdɪfrənt ˈvedʒtəbəlz ən nʌts/", "description": "different结尾的/t/与vegetables开头的/v/相邻，发生不完全爆破；vegetables结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/。"},
        {"words": "especially those with", "phonetic": "/ɪˈspeʃəli ðoʊz wɪð/", "description": "especially结尾的/i/与those开头的/ð/发生辅元连读；those结尾的/z/与with开头的/w/发生辅音连读。"},
        {"words": "high amounts of protein", "phonetic": "/haɪ əˈmaʊnts əv ˈproʊtin/", "description": "high结尾的/aɪ/与amounts开头的/ə/发生元元连读；amounts结尾的/s/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与protein开头的/p/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Apparently / that's no problem. / He eats a variety of / different vegetables and nuts, / especially those / with high amounts of protein.",
        "explanation": "评注副词(Apparently)/主句(that's no problem)/第二句主语+谓语+宾语(He eats a variety of)/宾语修饰语(different vegetables and nuts)/强调副词(especially those)/后置定语(with high amounts of protein)，评注副词独立成意群以体现口语中的前置停顿。",
    },
}

DATA["He's an animal activist. He's always been very sensitive and sympathizes with animals."] = {
    "connected_speech": [
        {"words": "He's an animal activist", "phonetic": "/hiz ən ˈænɪməl ˈæktɪvɪst/", "description": "He's结尾的/z/与an的/ən/发生辅元连读；an结尾的/n/与animal开头的/æ/发生辅元连读；animal结尾的/l/与activist开头的/æ/发生辅元连读。"},
        {"words": "He's always been", "phonetic": "/hiz ˈɔlweɪz bin/", "description": "He's结尾的/z/与always开头的/ɔ/发生辅元连读；always结尾的/z/与been开头的/b/发生辅音连读。"},
        {"words": "very sensitive and", "phonetic": "/ˈveri ˈsensɪtɪv ən/", "description": "sensitive结尾的/v/与and的/ən/发生辅元连读；and弱读为/ən/。"},
        {"words": "sympathizes with animals", "phonetic": "/ˈsɪmpəθaɪzɪz wɪð ˈænɪməlz/", "description": "sympathizes结尾的/z/与with开头的/w/发生辅音连读；with结尾的/ð/与animals开头的/æ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "He's an animal activist. / He's always been / very sensitive / and sympathizes with animals.",
        "explanation": "第一句(He's an animal activist)/第二句主语+谓语(He's always been)/表语1(very sensitive)/并列谓语+宾语(and sympathizes with animals)，按讲话的自然节奏和信息焦点分组。",
    },
}

DATA["He says that keeping animals in zoos and parks causes them great distress."] = {
    "connected_speech": [
        {"words": "He says that keeping", "phonetic": "/hi sez ðət ˈkipɪŋ/", "description": "says结尾的/z/与that开头的/ð/发生辅音连读；that弱读为/ðət/，结尾的/t/与keeping开头的/k/相邻，发生不完全爆破。"},
        {"words": "animals in zoos and parks", "phonetic": "/ˈænɪməlz ɪn zuz ən pɑks/", "description": "animals结尾的/z/与in开头的/ɪ/发生辅元连读；in结尾的/n/与zoos开头的/z/发生辅元连读；zoos结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/，结尾的/n/与parks开头的/p/发生辅元连读。"},
        {"words": "causes them great distress", "phonetic": "/ˈkɔzɪz ðəm ɡreɪt dɪˈstres/", "description": "causes结尾的/z/与them开头的/ð/发生辅音连读；them弱读为/ðəm/；great结尾的/t/与distress开头的/d/相邻，发生不完全爆破（失爆）。"},
    ],
    "sense_groups": {
        "segmented": "He says / that keeping animals / in zoos and parks / causes them / great distress.",
        "explanation": "主句(He says)/宾语从句主语(that keeping animals)/地点状语(in zoos and parks)/宾语从句谓语+宾语(causes them)/宾语补足语(great distress)，按从句内部主语-状语-谓语-宾补的逻辑结构划分。",
    },
}

DATA["Not all zoos and animal parks have the most favorable conditions, but without them it just wouldn't be feasible to learn about animals."] = {
    "connected_speech": [
        {"words": "Not all zoos and animal parks", "phonetic": "/nɑt ɔl zuz ən ˈænɪməl pɑks/", "description": "not结尾的/t/与all开头的/ɔ/发生辅元连读；all结尾的/l/与zoos开头的/z/发生辅元连读；zoos结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/。"},
        {"words": "have the most favorable conditions", "phonetic": "/həv ðə moʊst ˈfeɪvərəbəl kənˈdɪʃənz/", "description": "have弱读为/həv/，结尾的/v/与the的/ðə/发生辅元连读；most结尾的/t/与favorable开头的/f/相邻，发生不完全爆破；favorable结尾的/l/与conditions开头的/k/发生辅元连读。"},
        {"words": "but without them", "phonetic": "/bət wɪˈðaʊt ðəm/", "description": "but结尾的/t/与without开头的/w/相邻，发生不完全爆破（失爆）；without结尾的/t/与them开头的/ð/相邻，发生不完全爆破；them弱读为/ðəm/。"},
        {"words": "it just wouldn't be feasible", "phonetic": "/ɪt dʒʌst ˈwʊdnt bi ˈfizəbəl/", "description": "it结尾的/t/与just开头的/dʒ/相邻，发生不完全爆破；just结尾的/t/与wouldn't开头的/w/相邻，发生不完全爆破；wouldn't结尾的/t/与be开头的/b/相邻，发生不完全爆破。"},
        {"words": "to learn about animals", "phonetic": "/tə lɜrn əˈbaʊt ˈænɪməlz/", "description": "to弱读为/tə/，与learn开头的/l/发生辅元连读；learn结尾的/n/与about开头的/ə/发生辅元连读；about结尾的/t/与animals开头的/æ/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Not all zoos and animal parks / have the most favorable conditions, / but without them / it just wouldn't be feasible / to learn about animals.",
        "explanation": "主语(Not all zoos and animal parks)/谓语+宾语(have the most favorable conditions)/转折状语(but without them)/主句(it just wouldn't be feasible)/主语补足语(to learn about animals)，按让步-转折逻辑和句法结构划分。",
    },
}

DATA["I don't think I could ever give up a good hot dog at a baseball game."] = {
    "connected_speech": [
        {"words": "I don't think I could", "phonetic": "/aɪ doʊnt θɪŋk aɪ kʊd/", "description": "don't结尾的/t/与think开头的/θ/相邻，发生不完全爆破（失爆）；think结尾的/k/与I开头的/aɪ/发生辅元连读；I结尾的/aɪ/与could开头的/k/发生元辅连读。"},
        {"words": "ever give up a", "phonetic": "/ˈevər ɡɪv ʌp ə/", "description": "ever结尾的/r/与give开头的/ɡ/发生辅元连读(r连读)；give结尾的/v/与up开头的/ʌ/发生辅元连读；up结尾的/p/与a的/ə/发生辅元连读。"},
        {"words": "good hot dog", "phonetic": "/ɡʊd hɑt dɑɡ/", "description": "good结尾的/d/与hot开头的/h/相邻，发生不完全爆破；hot结尾的/t/与dog开头的/d/相邻，发生不完全爆破（失爆）。"},
        {"words": "at a baseball game", "phonetic": "/ət ə ˈbeɪsbɔl ɡeɪm/", "description": "at弱读为/ət/，结尾的/t/与a的/ə/发生辅元连读；a的/ə/与baseball开头的/b/发生辅元连读；baseball结尾的/l/与game开头的/ɡ/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "I don't think / I could ever give up / a good hot dog / at a baseball game.",
        "explanation": "主句主语+谓语(I don't think)/宾语从句主语+谓语(I could ever give up)/宾语(a good hot dog)/地点状语(at a baseball game)，按主从关系和宾语从句内部结构划分。",
    },
}

DATA["Did you see that television program on air travel last night?"] = {
    "connected_speech": [
        {"words": "Did you see that", "phonetic": "/dɪd ju si ðət/", "description": "did结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与see开头的/s/发生辅元连读；that弱读为/ðət/。"},
        {"words": "television program", "phonetic": "/ˈtelɪvɪʒən ˈproʊɡræm/", "description": "television结尾的/n/与program开头的/p/发生辅元连读。"},
        {"words": "on air travel", "phonetic": "/ɑn er ˈtrævəl/", "description": "on结尾的/n/与air开头的/er/发生辅元连读；air结尾的/r/与travel开头的/t/发生辅元连读（r连读）。"},
        {"words": "last night", "phonetic": "/læst naɪt/", "description": "last结尾的/t/与night开头的/n/相邻，发生不完全爆破（失爆）。"},
    ],
    "sense_groups": {
        "segmented": "Did you see / that television program / on air travel / last night?",
        "explanation": "疑问助词+主语+谓语(Did you see)/宾语(that television program)/主题状语(on air travel)/时间状语(last night)，按疑问句的信息结构逐步展开划分。",
    },
}

DATA["I was surprised that the expert recommended not eating for the entire journey and avoiding sleeping on the plane."] = {
    "connected_speech": [
        {"words": "I was surprised that", "phonetic": "/aɪ wəz səˈpraɪzd ðət/", "description": "was弱读为/wəz/，结尾的/z/与surprised开头的/s/相邻，可合并延长；surprised结尾的/d/与that开头的/ð/相邻，发生不完全爆破；that弱读为/ðət/。"},
        {"words": "the expert recommended", "phonetic": "/ði ˈekspɜrt ˌrekəˈmendɪd/", "description": "the在元音前读/ði/，与expert开头的/e/发生元元连读；expert结尾的/t/与recommended开头的/r/发生辅元连读。"},
        {"words": "not eating for the entire journey", "phonetic": "/nɑt ˈitɪŋ fər ði ɪnˈtaɪr ˈdʒɜrni/", "description": "not结尾的/t/与eating开头的/i/发生辅元连读；eating结尾的/ŋ/与for开头的/f/发生辅元连读；for弱读为/fər/；the在元音前读/ði/。"},
        {"words": "and avoiding sleeping", "phonetic": "/ən əˈvɔɪdɪŋ ˈslipɪŋ/", "description": "and弱读为/ən/，结尾的/n/与avoiding开头的/ə/发生辅元连读；avoiding结尾的/ŋ/与sleeping开头的/s/发生辅元连读。"},
        {"words": "on the plane", "phonetic": "/ɑn ðə pleɪn/", "description": "on结尾的/n/与the的/ðə/发生辅元连读；the弱读为/ðə/，与plane开头的/p/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "I was surprised / that the expert recommended / not eating / for the entire journey / and avoiding sleeping / on the plane.",
        "explanation": "主句(I was surprised)/宾语从句主语+谓语(that the expert recommended)/宾语1(not eating)/时间状语(for the entire journey)/并列宾语(and avoiding sleeping)/地点状语(on the plane)，按从句的宾语并列结构和各自修饰语划分。",
    },
}

DATA["I read an article on the subject in the past that suggested the opposite — that it was important not to miss meals."] = {
    "connected_speech": [
        {"words": "I read an article", "phonetic": "/aɪ red ən ˈɑtɪkəl/", "description": "read结尾的/d/与an的/ən/发生辅元连读；an结尾的/n/与article开头的/ɑ/发生辅元连读。"},
        {"words": "on the subject in the past", "phonetic": "/ɑn ðə ˈsʌbdʒɪkt ɪn ðə pæst/", "description": "on结尾的/n/与the的/ðə/发生辅元连读；subject结尾的/t/与in开头的/ɪ/发生辅元连读；in结尾的/n/与the的/ðə/发生辅元连读。"},
        {"words": "that suggested the opposite", "phonetic": "/ðət səˈdʒestɪd ði ˈɑpəzɪt/", "description": "that弱读为/ðət/；suggested结尾的/d/与the的/ði/相邻，发生不完全爆破；the在元音前读/ði/，与opposite的/ɑ/发生元元连读。"},
        {"words": "that it was important", "phonetic": "/ðət ɪt wəz ɪmˈpɔtənt/", "description": "that弱读为/ðət/，结尾的/t/与it开头的/ɪ/发生辅元连读；it结尾的/t/与was开头的/w/相邻，发生不完全爆破；was弱读为/wəz/。"},
        {"words": "not to miss meals", "phonetic": "/nɑt tə mɪs milz/", "description": "not结尾的/t/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/；miss结尾的/s/与meals开头的/m/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "I read an article / on the subject / in the past / that suggested the opposite — / that it was important / not to miss meals.",
        "explanation": "主句(I read an article)/主题状语(on the subject)/时间状语(in the past)/定语从句(that suggested the opposite)/同位语从句(that it was important)/主语补足语(not to miss meals)，破折号处为强调停顿，同位语从句单独成组。",
    },
}

DATA["Well, the expert on the show did cite research supporting her recommendations, so I guess I'll give it a try next time."] = {
    "connected_speech": [
        {"words": "the expert on the show", "phonetic": "/ði ˈekspɜrt ɑn ðə ʃoʊ/", "description": "the在元音前读/ði/，与expert的/e/发生元元连读；expert结尾的/t/与on开头的/ɑ/发生辅元连读；on结尾的/n/与the的/ðə/发生辅元连读。"},
        {"words": "did cite research", "phonetic": "/dɪd saɪt rɪˈsɜrtʃ/", "description": "did结尾的/d/与cite开头的/s/相邻，发生不完全爆破（失爆）；cite结尾的/t/与research开头的/r/发生辅元连读。"},
        {"words": "supporting her recommendations", "phonetic": "/səˈpɔtɪŋ hər ˌrekəmenˈdeɪʃənz/", "description": "supporting结尾的/ŋ/与her开头的/h/发生辅元连读；her弱读为/hər/，结尾的/r/与recommendations开头的/r/可合并或轻微延长。"},
        {"words": "so I guess I'll", "phonetic": "/soʊ aɪ ɡes aɪl/", "description": "so结尾的/oʊ/与I开头的/aɪ/发生元元连读；guess结尾的/s/与I'll开头的/aɪ/发生辅元连读。"},
        {"words": "give it a try next time", "phonetic": "/ɡɪv ɪt ə traɪ nekst taɪm/", "description": "give结尾的/v/与it开头的/ɪ/发生辅元连读；it结尾的/t/与a的/ə/发生辅元连读；next结尾的/t/与time开头的/t/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Well, / the expert on the show / did cite research / supporting her recommendations, / so I guess / I'll give it a try / next time.",
        "explanation": "话语标记(Well)/主语(the expert on the show)/谓语+宾语(did cite research)/伴随状语(supporting her recommendations)/结果连词+主句(so I guess)/宾语从句(I'll give it a try)/时间状语(next time)，Well前置独立成组，体现口语自然停顿。",
    },
}

DATA["Jet lag is a big problem for me and has been for the last few years even though I never suffered from it before."] = {
    "connected_speech": [
        {"words": "Jet lag is a big problem", "phonetic": "/dʒet læɡ ɪz ə bɪɡ ˈprɑbləm/", "description": "jet结尾的/t/与lag开头的/l/相邻，发生不完全爆破（失爆）；lag结尾的/ɡ/与is开头的/ɪ/发生辅元连读；is结尾的/z/与a的/ə/发生辅元连读；big结尾的/ɡ/与problem开头的/p/相邻，发生不完全爆破。"},
        {"words": "for me and has been", "phonetic": "/fər mi ən həz bin/", "description": "for弱读为/fər/；me结尾的/i/与and的/ən/发生辅元连读；and弱读为/ən/；has弱读为/həz/。"},
        {"words": "for the last few years", "phonetic": "/fər ðə læst fju jɪrz/", "description": "for弱读为/fər/；last结尾的/t/与few开头的/f/相邻，发生不完全爆破；few结尾的/u/与years开头的/j/发生元元连读。"},
        {"words": "even though I never", "phonetic": "/ˈivən ðoʊ aɪ ˈnevər/", "description": "even结尾的/n/与though开头的/ð/发生辅元连读；though结尾的/oʊ/与I开头的/aɪ/发生元元连读；never结尾的/r/在美式中可与后续元音发生r连读。"},
        {"words": "suffered from it before", "phonetic": "/ˈsʌfəd frəm ɪt bɪˈfɔr/", "description": "suffered结尾的/d/与from开头的/f/相邻，发生不完全爆破；from弱读为/frəm/，结尾的/m/与it开头的/ɪ/发生辅元连读；it结尾的/t/与before开头的/b/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Jet lag / is a big problem for me / and has been / for the last few years / even though / I never suffered from it before.",
        "explanation": "主语(Jet lag)/谓语+表语+状语(is a big problem for me)/并列谓语(and has been)/时间状语(for the last few years)/让步连词(even though)/让步从句(I never suffered from it before)，按让步主从结构和并列谓语划分。",
    },
}

DATA["She did say that jet lag often becomes more of a problem after 40, so I guess I'm lucky that I can still adjust."] = {
    "connected_speech": [
        {"words": "She did say that", "phonetic": "/ʃi dɪd seɪ ðət/", "description": "did结尾的/d/与say开头的/s/相邻，发生不完全爆破（失爆）；say结尾的/eɪ/与that的/ðət/发生元辅连读；that弱读为/ðət/。"},
        {"words": "jet lag often becomes", "phonetic": "/dʒet læɡ ˈɑfən bɪˈkʌmz/", "description": "jet结尾的/t/与lag开头的/l/相邻，发生不完全爆破；lag结尾的/ɡ/与often开头的/ɑ/发生辅元连读；often结尾的/n/与becomes开头的/b/发生辅元连读。"},
        {"words": "more of a problem after 40", "phonetic": "/mɔr əv ə ˈprɑbləm ˈæftər ˈfɔti/", "description": "more结尾的/r/与of开头的/ə/发生r连读；of弱读为/əv/，结尾的/v/与a的/ə/发生辅元连读；problem结尾的/m/与after开头的/ɑ/发生辅元连读；after结尾的/r/与40的/ˈfɔːti/首音/f/发生r连读。"},
        {"words": "so I guess I'm lucky", "phonetic": "/soʊ aɪ ɡes aɪm ˈlʌki/", "description": "so结尾的/oʊ/与I开头的/aɪ/发生元元连读；guess结尾的/s/与I'm开头的/aɪ/发生辅元连读。"},
        {"words": "that I can still adjust", "phonetic": "/ðət aɪ kən stɪl əˈdʒʌst/", "description": "that弱读为/ðət/，结尾的/t/与I开头的/aɪ/发生辅元连读；can弱读为/kən/；still结尾的/l/与adjust开头的/ə/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "She did say / that jet lag often becomes / more of a problem / after 40, / so I guess / I'm lucky / that I can still adjust.",
        "explanation": "主句(She did say)/宾语从句主语+谓语(that jet lag often becomes)/表语(more of a problem)/时间状语(after 40)/结果连词+主句(so I guess)/宾语从句(I'm lucky)/原因状语从句(that I can still adjust)，按多层从句的嵌入关系逐层划分。",
    },
}

DATA["Actually, my mother is terrified of airplanes to the point where she can't even fly, so our family vacations were always by car or train."] = {
    "connected_speech": [
        {"words": "my mother is terrified", "phonetic": "/maɪ ˈmʌðər ɪz ˈterɪfaɪd/", "description": "mother结尾的/r/与is开头的/ɪ/发生r连读（辅元连读）；is结尾的/z/与terrified开头的/t/发生辅音连读。"},
        {"words": "of airplanes", "phonetic": "/əv ˈerpleɪnz/", "description": "of弱读为/əv/，结尾的/v/与airplanes开头的/er/发生辅元连读。"},
        {"words": "to the point where", "phonetic": "/tə ðə pɔɪnt wer/", "description": "to弱读为/tə/，与the的/ðə/发生辅元连读；point结尾的/t/与where开头的/w/相邻，发生不完全爆破（失爆）。"},
        {"words": "she can't even fly", "phonetic": "/ʃi kænt ˈivən flaɪ/", "description": "can't结尾的/t/与even开头的/i/发生辅元连读；even结尾的/n/与fly开头的/f/发生辅元连读。"},
        {"words": "so our family vacations", "phonetic": "/soʊ aʊr ˈfæmɪli veɪˈkeɪʃənz/", "description": "so结尾的/oʊ/与our的/aʊr/发生元元连读；our结尾的/r/与family开头的/f/发生r连读（辅元连读）。"},
        {"words": "were always by car or train", "phonetic": "/wər ˈɔlweɪz baɪ kɑr ɔr treɪn/", "description": "were弱读为/wər/，结尾的/r/与always开头的/ɔ/发生r连读；always结尾的/z/与by开头的/b/发生辅音连读；by结尾的/aɪ/与car开头的/k/发生辅元连读；car结尾的/r/与or开头的/ɔ/发生r连读；or结尾的/r/与train开头的/t/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "Actually, / my mother / is terrified of airplanes / to the point / where she can't even fly, / so our family vacations / were always by car or train.",
        "explanation": "话语标记(Actually)/主语(my mother)/谓语+表语+状语(is terrified of airplanes)/程度状语(to the point)/定语从句(where she can't even fly)/结果连词+主语(so our family vacations)/谓语+方式状语(were always by car or train)，Actually前置成组，其余按因-果和修饰关系划分。",
    },
}

DATA["I just get anxious before I fly and feel nervous the whole time we're in the air."] = {
    "connected_speech": [
        {"words": "I just get anxious", "phonetic": "/aɪ dʒʌst ɡet ˈæŋkʃəs/", "description": "just结尾的/t/与get开头的/ɡ/相邻，发生不完全爆破（失爆）；get结尾的/t/与anxious开头的/æ/发生辅元连读。"},
        {"words": "before I fly", "phonetic": "/bɪˈfɔr aɪ flaɪ/", "description": "before结尾的/r/与I开头的/aɪ/发生r连读（辅元连读）；I结尾的/aɪ/与fly开头的/f/发生元辅连读。"},
        {"words": "and feel nervous", "phonetic": "/ən fil ˈnɜrvəs/", "description": "and弱读为/ən/，结尾的/n/与feel开头的/f/发生辅元连读；feel结尾的/l/与nervous开头的/n/发生辅音连读。"},
        {"words": "the whole time", "phonetic": "/ðə hoʊl taɪm/", "description": "the弱读为/ðə/，与whole开头的/h/发生辅元连读（h可弱读省略）；whole结尾的/l/与time开头的/t/发生辅音连读。"},
        {"words": "we're in the air", "phonetic": "/wɪr ɪn ði er/", "description": "we're结尾的/r/与in开头的/ɪ/发生r连读；in结尾的/n/与the的/ði/发生辅元连读；the在元音前读/ði/，与air的/er/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "I just get anxious / before I fly / and feel nervous / the whole time / we're in the air.",
        "explanation": "主句(I just get anxious)/时间状语从句(before I fly)/并列谓语+表语(and feel nervous)/时间状语(the whole time)/定语从句(we're in the air)，按并列结构和时间逻辑层次划分。",
    },
}

DATA["The expert said 20% of people are afraid to fly, but actually it was a quarter of people, so the problem really is widespread."] = {
    "connected_speech": [
        {"words": "The expert said 20%", "phonetic": "/ði ˈekspɜrt sed ˈtwenti pəˈsent/", "description": "the在元音前读/ði/；expert结尾的/t/与said开头的/s/相邻，发生不完全爆破（失爆）；said结尾的/d/与20%开头的/t/相邻，发生不完全爆破。"},
        {"words": "of people are afraid to fly", "phonetic": "/əv ˈpipəl ər əˈfreɪd tə flaɪ/", "description": "of弱读为/əv/，结尾的/v/与people开头的/p/发生辅音连读；people结尾的/l/与are开头的/ɑ/发生辅元连读；are弱读为/ər/；afraid结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "but actually it was", "phonetic": "/bət ˈæktʃuəli ɪt wəz/", "description": "but结尾的/t/与actually开头的/æ/发生辅元连读；actually结尾的/i/与it开头的/ɪ/发生元元连读；it结尾的/t/与was开头的/w/相邻，发生不完全爆破；was弱读为/wəz/。"},
        {"words": "a quarter of people", "phonetic": "/ə ˈkwɔtər əv ˈpipəl/", "description": "quarter结尾的/r/与of开头的/ə/发生r连读；of弱读为/əv/。"},
        {"words": "so the problem really is widespread", "phonetic": "/soʊ ðə ˈprɑbləm ˈrɪrli ɪz ˈwaɪdspred/", "description": "so结尾的/oʊ/与the的/ðə/发生元辅连读；problem结尾的/m/与really开头的/r/发生辅元连读；really结尾的/i/与is开头的/ɪ/发生元元连读；is结尾的/z/与widespread开头的/w/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "The expert said / 20% of people / are afraid to fly, / but actually / it was a quarter of people, / so the problem / really is widespread.",
        "explanation": "主句(The expert said)/宾语从句主语(20% of people)/谓语+表语+状语(are afraid to fly)/转折副词(but actually)/并列主句(it was a quarter of people)/结果连词+主语(so the problem)/谓语+表语(really is widespread)，按并列-转折-结果的复合逻辑关系划分。",
    },
}

# ─── cet4-2025-12 Section C: Passages ───

DATA["Nothing can substitute real world experience when it comes to getting started in user experience design."] = {
    "connected_speech": [
        {"words": "Nothing can substitute", "phonetic": "/ˈnʌθɪŋ kæn ˈsʌbstɪtjut/", "description": "Nothing结尾的/ŋ/与can开头的/k/发生辅元连读；can弱读为/kæn/，结尾的/n/与substitute开头的/s/发生辅元连读。"},
        {"words": "real world experience", "phonetic": "/rɪrl wɜrld ɪkˈspɪriəns/", "description": "real结尾的/l/与world开头的/w/发生辅音连读；world结尾的/d/与experience开头的/ɪ/相邻，发生不完全爆破（失爆）。"},
        {"words": "when it comes to", "phonetic": "/wen ɪt kʌmz tu/", "description": "when结尾的/n/与it开头的/ɪ/发生辅元连读；it结尾的/t/与comes开头的/k/相邻，发生不完全爆破（失爆）；comes结尾的/z/与to的/tu/发生辅音连读；to弱读为/tu/。"},
        {"words": "getting started in", "phonetic": "/ˈɡetɪŋ ˈstɑtɪd ɪn/", "description": "getting结尾的/ŋ/与started开头的/s/发生辅元连读；started结尾的/d/与in开头的/ɪ/发生辅元连读。"},
        {"words": "user experience design", "phonetic": "/ˈjuzə ɪkˈspɪriəns dɪˈzaɪn/", "description": "user结尾的/r/与experience开头的/ɪ/发生r连读（辅元连读）；experience结尾的/s/与design开头的/d/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Nothing can substitute / real world experience / when it comes to / getting started / in user experience design.",
        "explanation": "主语+谓语+情态(Nothing can substitute)/宾语(real world experience)/时间状语从句引导词(when it comes to)/动名词短语主语(getting started)/介词短语修饰语(in user experience design)，按主句-从句的逻辑层次和语义完整性划分。",
    },
}

DATA["Higher education is a great way to equip yourself with some core skills, but it will not prepare you for actual challenges with clients."] = {
    "connected_speech": [
        {"words": "Higher education is a great way", "phonetic": "/ˈhaɪr ˌedjuˈkeɪʃən ɪz ə ɡreɪt weɪ/", "description": "Higher结尾的/r/与education开头的/e/发生r连读；education结尾的/n/与is开头的/ɪ/发生辅元连读；is结尾的/z/与a的/ə/发生辅元连读；great结尾的/t/与way开头的/w/相邻，发生不完全爆破。"},
        {"words": "to equip yourself with", "phonetic": "/tu ɪˈkwɪp jəˈself wɪð/", "description": "to弱读为/tu/，结尾的/u/与equip开头的/ɪ/发生元元连读；equip结尾的/p/与yourself开头的/j/发生辅元连读；yourself结尾的/f/与with开头的/w/发生辅音连读。"},
        {"words": "some core skills", "phonetic": "/səm kɔr skɪlz/", "description": "some弱读为/səm/；core结尾的/r/与skills开头的/s/发生r连读（辅元连读）。"},
        {"words": "but it will not prepare you", "phonetic": "/bət ɪt wɪl nɑt prɪˈper ju/", "description": "but结尾的/t/与it开头的/ɪ/发生辅元连读；it结尾的/t/与will开头的/w/相邻，发生不完全爆破；not结尾的/t/与prepare开头的/p/相邻，发生不完全爆破；prepare结尾的/r/与you开头的/j/发生r连读。"},
        {"words": "for actual challenges", "phonetic": "/fər ˈæktʃuəl ˈtʃælɪndʒɪz/", "description": "for弱读为/fər/，结尾的/r/与actual开头的/æ/发生r连读；actual结尾的/l/与challenges开头的/tʃ/发生辅音连读。"},
        {"words": "with clients", "phonetic": "/wɪð ˈklaɪrnts/", "description": "with结尾的/ð/与clients开头的/k/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Higher education / is a great way / to equip yourself / with some core skills, / but it will not prepare you / for actual challenges / with clients.",
        "explanation": "主语(Higher education)/谓语+表语(is a great way)/不定式定语(to equip yourself)/方式状语(with some core skills)/转折连词+主句(but it will not prepare you)/目的状语(for actual challenges)/定语(with clients)，逗号处为分句界线和自然停顿点。",
    },
}

DATA["Being proficient with a design tool and a few methods doesn't make you a user experience designer."] = {
    "connected_speech": [
        {"words": "Being proficient with", "phonetic": "/ˈbiɪŋ prəˈfɪʃənt wɪð/", "description": "Being结尾的/ŋ/与proficient开头的/p/发生辅元连读；proficient结尾的/t/与with开头的/w/相邻，发生不完全爆破（失爆）。"},
        {"words": "a design tool", "phonetic": "/ə dɪˈzaɪn tul/", "description": "a弱读为/ə/，与design开头的/d/发生辅元连读；design结尾的/n/与tool开头的/t/发生辅元连读。"},
        {"words": "and a few methods", "phonetic": "/ən ə fju ˈmeθədz/", "description": "and弱读为/ən/，结尾的/n/与a的/ə/发生辅元连读；few结尾的/u/与methods开头的/m/发生辅元连读。"},
        {"words": "doesn't make you", "phonetic": "/ˈdʌznt meɪk ju/", "description": "doesn't结尾的/t/与make开头的/m/相邻，发生不完全爆破；make结尾的/k/与you开头的/j/发生辅元连读。"},
        {"words": "a user experience designer", "phonetic": "/ə ˈjuzə ɪkˈspɪriəns dɪˈzaɪnər/", "description": "user结尾的/r/与experience开头的/ɪ/发生r连读；experience结尾的/s/与designer开头的/d/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Being proficient / with a design tool / and a few methods / doesn't make you / a user experience designer.",
        "explanation": "动名词主语(Being proficient)/介词短语1(with a design tool)/并列介词短语(and a few methods)/谓语(doesn't make you)/宾语(a user experience designer)，按主语-修饰语-谓语-宾语的语法结构划分。",
    },
}

DATA["There simply isn't a one size fits all process. Being effective requires adaptability, something you don't really learn in school."] = {
    "connected_speech": [
        {"words": "There simply isn't", "phonetic": "/ðer ˈsɪmpli ˈɪznt/", "description": "There结尾的/r/与simply开头的/s/发生r连读；simply结尾的/i/与isn't开头的/ɪ/发生元元连读。"},
        {"words": "a one size fits all process", "phonetic": "/ə wʌn saɪz fɪts ɔl ˈproʊses/", "description": "one结尾的/n/与size开头的/s/发生辅元连读；size结尾的/z/与fits开头的/f/发生辅音连读；fits结尾的/s/与all开头的/ɔ/发生辅元连读。"},
        {"words": "Being effective requires adaptability", "phonetic": "/ˈbiɪŋ ɪˈfektɪv rɪˈkwaɪrz əˌdæptəˈbɪlɪti/", "description": "Being结尾的/ŋ/与effective开头的/ɪ/发生辅元连读；effective结尾的/v/与requires开头的/r/发生辅音连读；requires结尾的/z/与adaptability开头的/ə/发生辅元连读。"},
        {"words": "something you don't really learn", "phonetic": "/ˈsʌmθɪŋ ju doʊnt ˈrɪrli lɜrn/", "description": "something结尾的/ŋ/与you开头的/j/发生辅元连读；don't结尾的/t/与really开头的/r/相邻，发生不完全爆破；really结尾的/i/与learn开头的/l/发生辅元连读。"},
        {"words": "in school", "phonetic": "/ɪn skul/", "description": "in结尾的/n/与school开头的/s/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "There simply isn't / a one size fits all process. / Being effective / requires adaptability, / something / you don't really learn / in school.",
        "explanation": "第一句主谓(There simply isn't)/主语(a one size fits all process)/第二句主语(Being effective)/谓语+宾语(requires adaptability)/同位语(something)/定语从句(you don't really learn)/地点状语(in school)，句号处为大停顿，同位语独立成组。",
    },
}

DATA["I found my way to user experience through graphic design and slowly over many different roles and experiences."] = {
    "connected_speech": [
        {"words": "I found my way to", "phonetic": "/aɪ faʊnd maɪ weɪ tu/", "description": "found结尾的/d/与my开头的/m/相邻，发生不完全爆破（失爆）；way结尾的/eɪ/与to的/tu/发生元辅连读；to弱读为/tu/。"},
        {"words": "user experience", "phonetic": "/ˈjuzər ɪkˈspɪriəns/", "description": "user结尾的/r/与experience开头的/ɪ/发生r连读（辅元连读）。"},
        {"words": "through graphic design", "phonetic": "/θru ˈɡræfɪk dɪˈzaɪn/", "description": "through结尾的/u/与graphic开头的/ɡ/发生辅元连读；graphic结尾的/k/与design开头的/d/相邻，发生不完全爆破。"},
        {"words": "and slowly over many", "phonetic": "/ən ˈsloʊli ˈoʊvər ˈmeni/", "description": "and弱读为/ən/，结尾的/n/与slowly开头的/s/发生辅元连读；slowly结尾的/i/与over开头的/oʊ/发生元元连读；over结尾的/r/与many开头的/m/发生辅元连读(r连读)。"},
        {"words": "different roles and experiences", "phonetic": "/ˈdɪfrənt roʊlz ən ɪkˈspɪriənsɪz/", "description": "different结尾的/t/与roles开头的/r/发生辅元连读；roles结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/。"},
    ],
    "sense_groups": {
        "segmented": "I found my way / to user experience / through graphic design / and slowly / over many different roles / and experiences.",
        "explanation": "主句(I found my way)/目标状语(to user experience)/方式状语1(through graphic design)/连接词+方式状语2(and slowly)/伴随状语(over many different roles)/并列宾语(and experiences)，按动作实现的路径和方式逐层展开。",
    },
}

DATA["It took time and commitment to continue to pursue roles within teams that I knew could teach and challenge me."] = {
    "connected_speech": [
        {"words": "It took time and commitment", "phonetic": "/ɪt tʊk taɪm ən kəˈmɪtmənt/", "description": "it结尾的/t/与took开头的/t/相邻，发生不完全爆破；took结尾的/k/与time开头的/t/相邻，发生不完全爆破；and弱读为/ən/。"},
        {"words": "to continue to pursue roles", "phonetic": "/tə kənˈtɪnju tə pəˈsju roʊlz/", "description": "to弱读为/tə/，与continue开头的/k/发生辅元连读；continue结尾的/u/与to的/tə/发生辅元连读；pursue结尾的/u/与roles开头的/r/发生辅元连读。"},
        {"words": "within teams", "phonetic": "/wɪˈðɪn timz/", "description": "within结尾的/n/与teams开头的/t/发生辅元连读。"},
        {"words": "that I knew could teach", "phonetic": "/ðət aɪ nju kʊd titʃ/", "description": "that弱读为/ðət/，结尾的/t/与I开头的/aɪ/发生辅元连读；knew结尾的/u/与could开头的/k/发生辅元连读；could结尾的/d/与teach开头的/t/相邻，发生不完全爆破。"},
        {"words": "and challenge me", "phonetic": "/ən ˈtʃælɪndʒ mi/", "description": "and弱读为/ən/，结尾的/n/与challenge开头的/tʃ/发生辅元连读；challenge结尾的/dʒ/与me开头的/m/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "It took time and commitment / to continue / to pursue roles / within teams / that I knew / could teach and challenge me.",
        "explanation": "主句(It took time and commitment)/主语补足语(to continue)/目的状语(to pursue roles)/范围状语(within teams)/定语从句主语(that I knew)/定语从句谓语+宾语(could teach and challenge me)，形式主语句式中真主语后置，各意群按语义层次展开。",
    },
}

DATA["You can start anywhere as long as you know your end goal and you commit to actively pursue opportunities to learn and grow."] = {
    "connected_speech": [
        {"words": "You can start anywhere", "phonetic": "/ju kæn stɑt ˈeniwer/", "description": "can弱读为/kæn/，结尾的/n/与start开头的/s/发生辅元连读；start结尾的/t/与anywhere开头的/e/发生辅元连读。"},
        {"words": "as long as you know", "phonetic": "/əz lɑŋ əz ju noʊ/", "description": "as弱读为/əz/，结尾的/z/与long开头的/l/发生辅元连读；long结尾的/ŋ/与as的/əz/发生辅元连读；as结尾的/z/与you开头的/j/发生辅音连读。"},
        {"words": "your end goal", "phonetic": "/jər end ɡoʊl/", "description": "your弱读为/jər/；end结尾的/d/与goal开头的/ɡ/相邻，发生不完全爆破（失爆）。"},
        {"words": "and you commit to actively", "phonetic": "/ən ju kəˈmɪt tu ˈæktɪvli/", "description": "and弱读为/ən/，结尾的/n/与you开头的/j/发生辅元连读；commit结尾的/t/与to开头的/t/相邻，发生不完全爆破；to弱读为/tu/；actively结尾的/i/与pursue开头的/p/发生辅元连读。"},
        {"words": "pursue opportunities", "phonetic": "/pəˈsju ˌɑpəˈtjunɪtiz/", "description": "pursue结尾的/u/与opportunities开头的/ɑ/发生元元连读。"},
        {"words": "to learn and grow", "phonetic": "/tə lɜrn ən ɡroʊ/", "description": "to弱读为/tə/，与learn开头的/l/发生辅元连读；learn结尾的/n/与and的/ən/发生辅元连读；and弱读为/ən/。"},
    ],
    "sense_groups": {
        "segmented": "You can start anywhere / as long as / you know your end goal / and you commit / to actively pursue opportunities / to learn and grow.",
        "explanation": "主句(You can start anywhere)/条件连词(as long as)/条件从句1(you know your end goal)/并列条件从句2(and you commit)/目的状语(to actively pursue opportunities)/目的补语(to learn and grow)，按条件状语从句的复合结构和目的层次划分。",
    },
}

DATA["When planning for this year, our principal asked what needed to change to engage students more in their learning."] = {
    "connected_speech": [
        {"words": "When planning for this year", "phonetic": "/wen ˈplænɪŋ fər ðɪs jɪr/", "description": "when结尾的/n/与planning开头的/p/发生辅元连读；planning结尾的/ŋ/与for开头的/f/发生辅元连读；for弱读为/fər/；this结尾的/s/与year开头的/j/发生辅元连读。"},
        {"words": "our principal asked", "phonetic": "/aʊr ˈprɪnsɪpəl æskt/", "description": "our结尾的/r/与principal开头的/p/发生r连读（辅元连读）；principal结尾的/l/与asked开头的/ɑ/发生辅元连读。"},
        {"words": "what needed to change", "phonetic": "/wɑt ˈnidɪd tə tʃeɪndʒ/", "description": "what结尾的/t/与needed开头的/n/相邻，发生不完全爆破（失爆）；needed结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/，与change开头的/tʃ/发生辅元连读。"},
        {"words": "to engage students more", "phonetic": "/tu ɪnˈɡeɪdʒ ˈstjudənts mɔr/", "description": "to弱读为/tu/；engage结尾的/dʒ/与students开头的/s/发生辅音连读；students结尾的/s/与more开头的/m/发生辅音连读。"},
        {"words": "in their learning", "phonetic": "/ɪn ðer ˈlɜrnɪŋ/", "description": "in结尾的/n/与their开头的/ð/发生辅元连读；their结尾的/r/与learning开头的/l/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "When planning for this year, / our principal asked / what needed to change / to engage students more / in their learning.",
        "explanation": "时间状语(When planning for this year)/主句(our principal asked)/宾语从句(what needed to change)/目的状语(to engage students more)/范围状语(in their learning)，按状语前置-主句-宾语从句-补语的层次递进划分。",
    },
}

DATA["I responded in a whisper: flexible seating, thinking about our classroom with rows of desks and name plates."] = {
    "connected_speech": [
        {"words": "I responded in a whisper", "phonetic": "/aɪ rɪˈspɑndɪd ɪn ə ˈwɪspər/", "description": "responded结尾的/d/与in开头的/ɪ/发生辅元连读；in结尾的/n/与a的/ə/发生辅元连读。"},
        {"words": "flexible seating", "phonetic": "/ˈfleksɪbəl ˈsitɪŋ/", "description": "flexible结尾的/l/与seating开头的/s/发生辅音连读。"},
        {"words": "thinking about our classroom", "phonetic": "/ˈθɪŋkɪŋ əˈbaʊt aʊr ˈklæsrum/", "description": "thinking结尾的/ŋ/与about开头的/ə/发生辅元连读；about结尾的/t/与our开头的/aʊ/发生辅元连读；our结尾的/r/与classroom开头的/k/发生r连读（辅元连读）。"},
        {"words": "with rows of desks", "phonetic": "/wɪð roʊz əv desks/", "description": "with结尾的/ð/与rows开头的/r/发生辅音连读；rows结尾的/z/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与desks开头的/d/发生辅音连读。"},
        {"words": "and name plates", "phonetic": "/ən neɪm pleɪts/", "description": "and弱读为/ən/，结尾的/n/与name开头的/n/发生辅元连读（鼻音连读）；name结尾的/m/与plates开头的/p/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "I responded in a whisper: / flexible seating, / thinking about / our classroom / with rows of desks / and name plates.",
        "explanation": "主句(I responded in a whisper)/直接引语1(flexible seating)/伴随状语(thinking about)/宾语(our classroom)/介词短语定语(with rows of desks)/并列定语(and name plates)，冒号处为讲话内容的自然切分，之后按语义碎片分组。",
    },
}

DATA["Flexible seating has been defined as movable furniture to create an engaging learning environment."] = {
    "connected_speech": [
        {"words": "Flexible seating has been", "phonetic": "/ˈfleksɪbəl ˈsitɪŋ həz bin/", "description": "flexible结尾的/l/与seating开头的/s/发生辅音连读；seating结尾的/ŋ/与has开头的/h/发生辅元连读；has弱读为/həz/，结尾的/z/与been开头的/b/发生辅音连读。"},
        {"words": "defined as movable furniture", "phonetic": "/dɪˈfaɪnd əz ˈmuvəbəl ˈfɜrnɪtʃər/", "description": "defined结尾的/d/与as开头的/ə/发生辅元连读；as弱读为/əz/，结尾的/z/与movable开头的/m/发生辅音连读；movable结尾的/l/与furniture开头的/f/发生辅音连读。"},
        {"words": "to create an engaging", "phonetic": "/tə kriˈeɪt ən ɪnˈɡeɪdʒɪŋ/", "description": "to弱读为/tə/，与create开头的/k/发生辅元连读；create结尾的/t/与an的/ən/发生辅元连读；an结尾的/n/与engaging开头的/ɪ/发生辅元连读。"},
        {"words": "learning environment", "phonetic": "/ˈlɜrnɪŋ ɪnˈvaɪrənmənt/", "description": "learning结尾的/ŋ/与environment开头的/ɪ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Flexible seating / has been defined as / movable furniture / to create / an engaging learning environment.",
        "explanation": "主语(Flexible seating)/谓语(has been defined as)/宾语(movable furniture)/目的状语(to create)/宾语(an engaging learning environment)，按主-谓-宾-补的简洁结构和信息层级划分。",
    },
}

DATA["It is a shift in practice from being teacher focused to student focused learning."] = {
    "connected_speech": [
        {"words": "It is a shift in practice", "phonetic": "/ɪt ɪz ə ʃɪft ɪn ˈpræktɪs/", "description": "it结尾的/t/与is开头的/ɪ/发生辅元连读；is结尾的/z/与a的/ə/发生辅元连读；shift结尾的/t/与in开头的/ɪ/发生辅元连读；in结尾的/n/与practice开头的/p/发生辅元连读。"},
        {"words": "from being teacher focused", "phonetic": "/frəm ˈbiɪŋ ˈtitʃər ˈfoʊkəst/", "description": "from弱读为/frəm/，结尾的/m/与being开头的/b/发生辅元连读；being结尾的/ŋ/与teacher开头的/t/发生辅元连读；teacher结尾的/r/与focused开头的/f/发生辅元连读(r连读)。"},
        {"words": "to student focused learning", "phonetic": "/tə ˈstjudənt ˈfoʊkəst ˈlɜrnɪŋ/", "description": "to弱读为/tə/，与student开头的/s/发生辅元连读；student结尾的/t/与focused开头的/f/相邻，发生不完全爆破；focused结尾的/t/与learning开头的/l/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "It is a shift in practice / from being teacher focused / to student focused learning.",
        "explanation": "主句(It is a shift in practice)/来源状语(from being teacher focused)/目标状语(to student focused learning)，按转变的来源→目标的方向性逻辑划分。",
    },
}

DATA["For us, flexible seating has meant removing most of the traditional chairs and desks and introducing a variety of seating options."] = {
    "connected_speech": [
        {"words": "For us, flexible seating", "phonetic": "/fər ʌs ˈfleksɪbəl ˈsitɪŋ/", "description": "for弱读为/fər/，结尾的/r/与us开头的/ʌ/发生r连读；flexible结尾的/l/与seating开头的/s/发生辅音连读。"},
        {"words": "has meant removing", "phonetic": "/həz ment rɪˈmuvɪŋ/", "description": "has弱读为/həz/，结尾的/z/与meant开头的/m/发生辅音连读；meant结尾的/t/与removing开头的/r/发生辅元连读。"},
        {"words": "most of the traditional", "phonetic": "/moʊst əv ðə trəˈdɪʃənəl/", "description": "most结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/；the弱读为/ðə/；traditional结尾的/l/与chairs开头的/tʃ/发生辅音连读。"},
        {"words": "chairs and desks", "phonetic": "/tʃerz ən desks/", "description": "chairs结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/，结尾的/n/与desks开头的/d/发生辅元连读。"},
        {"words": "and introducing a variety of", "phonetic": "/ən ˌɪntrəˈdjusɪŋ ə vəˈraɪrti əv/", "description": "and弱读为/ən/，结尾的/n/与introducing开头的/ɪ/发生辅元连读；introducing结尾的/ŋ/与a的/ə/发生辅元连读；variety结尾的/i/与of的/ə/发生元元连读；of弱读为/əv/。"},
        {"words": "seating options", "phonetic": "/ˈsitɪŋ ˈɑpʃənz/", "description": "seating结尾的/ŋ/与options开头的/ɑ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "For us, / flexible seating / has meant / removing most of / the traditional chairs and desks / and introducing / a variety of seating options.",
        "explanation": "评注状语(For us)/主语(flexible seating)/谓语(has meant)/宾语1(removing most of)/宾语1修饰语(the traditional chairs and desks)/并列连词+宾语2(and introducing)/宾语2核心(a variety of seating options)，按主语-谓语-并列宾语的层次展开。",
    },
}

DATA["Teachers tend to still use the rows format because of either the need to control students or the belief that the teacher is the most important person."] = {
    "connected_speech": [
        {"words": "Teachers tend to still use", "phonetic": "/ˈtitʃərz tend tə stɪl juz/", "description": "Teachers结尾的/z/与tend开头的/t/发生辅音连读；tend结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/；still结尾的/l/与use开头的/j/发生辅音连读。"},
        {"words": "the rows format", "phonetic": "/ðə roʊz ˈfɔmæt/", "description": "the弱读为/ðə/，与rows开头的/r/发生辅元连读；rows结尾的/z/与format开头的/f/发生辅音连读。"},
        {"words": "because of either the need", "phonetic": "/bɪˈkɑz əv ˈaɪðər ðə nid/", "description": "because结尾的/z/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与either开头的/aɪ/发生辅元连读；either结尾的/r/与the的/ðə/发生r连读。"},
        {"words": "to control students", "phonetic": "/tə kənˈtroʊl ˈstjudənts/", "description": "to弱读为/tə/，与control开头的/k/发生辅元连读；control结尾的/l/与students开头的/s/发生辅音连读。"},
        {"words": "or the belief that the teacher", "phonetic": "/ɔr ðə bɪˈlif ðət ðə ˈtitʃər/", "description": "or结尾的/r/与the的/ðə/发生r连读；belief结尾的/f/与that的/ðət/发生辅音连读；that弱读为/ðət/。"},
        {"words": "is the most important person", "phonetic": "/ɪz ðə moʊst ɪmˈpɔtənt ˈpɜrsən/", "description": "is结尾的/z/与the的/ðə/发生辅元连读；the弱读为/ðə/；most结尾的/t/与important开头的/ɪ/发生辅元连读；important结尾的/t/与person开头的/p/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Teachers tend to still use / the rows format / because of either / the need to control students / or the belief / that the teacher / is the most important person.",
        "explanation": "主句(Teachers tend to still use)/宾语(the rows format)/原因状语引导(because of either)/原因选项1(the need to control students)/连接词+原因选项2(or the belief)/同位语从句主语(that the teacher)/表语(is the most important person)，按原因的两个选择分支划分，体现either...or结构。",
    },
}

DATA["Flexible seating enhances student ownership of space and engagement in learning while reducing rates of disengagement."] = {
    "connected_speech": [
        {"words": "Flexible seating enhances", "phonetic": "/ˈfleksɪbəl ˈsitɪŋ ɪnˈhɑnsɪz/", "description": "flexible结尾的/l/与seating开头的/s/发生辅音连读；seating结尾的/ŋ/与enhances开头的/ɪ/发生辅元连读。"},
        {"words": "student ownership of space", "phonetic": "/ˈstjudənt ˈoʊnəʃɪp əv speɪs/", "description": "student结尾的/t/与ownership开头的/oʊ/发生辅元连读；ownership结尾的/p/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与space开头的/s/发生辅音连读。"},
        {"words": "and engagement in learning", "phonetic": "/ən ɪnˈɡeɪdʒmənt ɪn ˈlɜrnɪŋ/", "description": "and弱读为/ən/，结尾的/n/与engagement开头的/ɪ/发生辅元连读；engagement结尾的/t/与in开头的/ɪ/发生辅元连读；in结尾的/n/与learning开头的/l/发生辅元连读。"},
        {"words": "while reducing rates of disengagement", "phonetic": "/waɪl rɪˈdjusɪŋ reɪts əv ˌdɪsɪnˈɡeɪdʒmənt/", "description": "while结尾的/l/与reducing开头的/r/发生辅音连读；reducing结尾的/ŋ/与rates开头的/r/发生辅元连读；rates结尾的/s/与of开头的/ə/发生辅元连读；of弱读为/əv/。"},
    ],
    "sense_groups": {
        "segmented": "Flexible seating enhances / student ownership of space / and engagement in learning / while reducing / rates of disengagement.",
        "explanation": "主语+谓语(Flexible seating enhances)/宾语1(student ownership of space)/并列宾语2(and engagement in learning)/伴随状语(while reducing)/状语宾语(rates of disengagement)，按谓语-双宾语-伴随状语的扩展结构划分。",
    },
}

DATA["Dozens of British students arriving for their first day of school on Tuesday were sent home over their shoes."] = {
    "connected_speech": [
        {"words": "Dozens of British students", "phonetic": "/ˈdʌzənz əv ˈbrɪtɪʃ ˈstjudənts/", "description": "Dozens结尾的/z/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与British开头的/b/发生辅音连读；British结尾的/ʃ/与students开头的/s/发生辅音连读。"},
        {"words": "arriving for their first day", "phonetic": "/əˈraɪvɪŋ fər ðer fɜrst deɪ/", "description": "arriving结尾的/ŋ/与for开头的/f/发生辅元连读；for弱读为/fər/；their结尾的/r/与first开头的/f/发生r连读；first结尾的/t/与day开头的/d/相邻，发生不完全爆破。"},
        {"words": "of school on Tuesday", "phonetic": "/əv skul ɑn ˈtjuzdeɪ/", "description": "of弱读为/əv/，结尾的/v/与school开头的/s/发生辅音连读；school结尾的/l/与on开头的/ɑ/发生辅元连读；on结尾的/n/与Tuesday开头的/t/发生辅元连读。"},
        {"words": "were sent home over their shoes", "phonetic": "/wər sent hoʊm ˈoʊvər ðer ʃuz/", "description": "were弱读为/wər/；sent结尾的/t/与home开头的/h/相邻，发生不完全爆破；home结尾的/m/与over开头的/oʊ/发生辅元连读；over结尾的/r/与their开头的/ð/发生r连读；their结尾的/r/与shoes开头的/ʃ/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "Dozens of British students / arriving for their first day / of school / on Tuesday / were sent home / over their shoes.",
        "explanation": "主语核心(Dozens of British students)/后置定语(arriving for their first day)/定语修饰(of school)/时间状语(on Tuesday)/谓语+状语(were sent home)/原因状语(over their shoes)，主语较长故将修饰语分列，谓语后状语独立成组。",
    },
}

DATA["About 30 students were turned away from Taverham high school in Norfolk due to a change in the school's uniform policy."] = {
    "connected_speech": [
        {"words": "About 30 students", "phonetic": "/əˈbaʊt ˈθɜrti ˈstjudənts/", "description": "About结尾的/t/与30开头的/θ/相邻，发生不完全爆破（失爆）；30结尾的/i/与students开头的/s/发生辅元连读。"},
        {"words": "were turned away from", "phonetic": "/wər tɜrnd əˈweɪ frəm/", "description": "were弱读为/wər/；turned结尾的/d/与away开头的/ə/发生辅元连读；away结尾的/eɪ/与from开头的/f/发生元辅连读；from弱读为/frəm/。"},
        {"words": "Taverham high school in Norfolk", "phonetic": "/ˈteɪvəhæm haɪ skul ɪn ˈnɔfək/", "description": "Taverham结尾的/m/与high开头的/h/发生辅元连读；high结尾的/aɪ/与school开头的/s/发生元辅连读；school结尾的/l/与in开头的/ɪ/发生辅元连读；in结尾的/n/与Norfolk开头的/n/可合并或轻微延长。"},
        {"words": "due to a change in", "phonetic": "/dju tu ə tʃeɪndʒ ɪn/", "description": "due结尾的/u/与to的/tu/发生元元连读；to弱读为/tu/；a的/ə/与change开头的/tʃ/发生辅元连读；change结尾的/dʒ/与in开头的/ɪ/发生辅元连读。"},
        {"words": "the school's uniform policy", "phonetic": "/ðə skulz ˈjunɪfɔm ˈpɑləsi/", "description": "the弱读为/ðə/；school's结尾的/z/与uniform开头的/j/发生辅音连读；uniform结尾的/m/与policy开头的/p/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "About 30 students / were turned away / from Taverham high school / in Norfolk / due to a change / in the school's uniform policy.",
        "explanation": "主语(About 30 students)/谓语+状语(were turned away)/地点状语1(from Taverham high school)/地点状语2(in Norfolk)/原因状语(due to a change)/原因状语修饰语(in the school's uniform policy)，按谁-做了什么-在哪里-为什么的逻辑链条划分。",
    },
}

DATA["The head teacher said he notified parents of the updated rules in an email in June."] = {
    "connected_speech": [
        {"words": "The head teacher said", "phonetic": "/ðə hed ˈtitʃə sed/", "description": "the弱读为/ðə/，与head开头的/h/发生辅元连读（h可弱读省略）；head结尾的/d/与teacher开头的/t/相邻，发生不完全爆破（失爆）；teacher结尾的/ə/与said开头的/s/发生辅元连读。"},
        {"words": "he notified parents", "phonetic": "/hi ˈnoʊtɪfaɪd ˈperənts/", "description": "he结尾的/i/与notified开头的/n/发生辅元连读；notified结尾的/d/与parents开头的/p/相邻，发生不完全爆破（失爆）。"},
        {"words": "of the updated rules", "phonetic": "/əv ðə ʌpˈdeɪtɪd rulz/", "description": "of弱读为/əv/，与the的/ðə/发生辅元连读；the弱读为/ðə/，与updated开头的/ʌ/发生元元连读；updated结尾的/d/与rules开头的/r/发生辅元连读。"},
        {"words": "in an email in June", "phonetic": "/ɪn ən ˈimeɪl ɪn dʒun/", "description": "in结尾的/n/与an的/ən/发生辅元连读；an结尾的/n/与email开头的/i/发生辅元连读；email结尾的/l/与in开头的/ɪ/发生辅元连读；in结尾的/n/与June开头的/dʒ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The head teacher said / he notified parents / of the updated rules / in an email / in June.",
        "explanation": "主句(The head teacher said)/宾语从句主谓宾(he notified parents)/宾语修饰语(of the updated rules)/方式状语(in an email)/时间状语(in June)，按主从关系和宾语从句内部的宾语-状语扩展顺序划分。",
    },
}

DATA["The price of school uniforms can spark panic among families struggling with the high cost of living."] = {
    "connected_speech": [
        {"words": "The price of school uniforms", "phonetic": "/ðə praɪs əv skul ˈjunɪfɔmz/", "description": "the弱读为/ðə/；price结尾的/s/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与school开头的/s/发生辅音连读；school结尾的/l/与uniforms开头的/j/发生辅音连读。"},
        {"words": "can spark panic among", "phonetic": "/kæn spɑk ˈpænɪk əˈmʌŋ/", "description": "can弱读为/kæn/，结尾的/n/与spark开头的/s/发生辅元连读；spark结尾的/k/与panic开头的/p/相邻，发生不完全爆破；panic结尾的/k/与among开头的/ə/发生辅元连读。"},
        {"words": "families struggling with", "phonetic": "/ˈfæmɪliz ˈstrʌɡlɪŋ wɪð/", "description": "families结尾的/z/与struggling开头的/s/相邻，可合并延长；struggling结尾的/ŋ/与with开头的/w/发生辅元连读。"},
        {"words": "the high cost of living", "phonetic": "/ðə haɪ kæst əv ˈlɪvɪŋ/", "description": "high结尾的/aɪ/与cost开头的/k/发生元辅连读；cost结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与living开头的/l/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "The price of school uniforms / can spark panic / among families / struggling with / the high cost of living.",
        "explanation": "主语(The price of school uniforms)/谓语+宾语(can spark panic)/范围状语(among families)/后置定语(struggling with)/定语宾语(the high cost of living)，按主-谓-宾-状-定的信息扩展顺序划分。",
    },
}

DATA["Nearly all British schools have uniforms. They cost parents an average of 337 pounds per year for each secondary school child."] = {
    "connected_speech": [
        {"words": "Nearly all British schools", "phonetic": "/ˈnɪrli ɔl ˈbrɪtɪʃ skulz/", "description": "Nearly结尾的/i/与all开头的/ɔ/发生元元连读；all结尾的/l/与British开头的/b/发生辅元连读；British结尾的/ʃ/与schools开头的/s/发生辅音连读。"},
        {"words": "have uniforms", "phonetic": "/həv ˈjunɪfɔmz/", "description": "have弱读为/həv/，结尾的/v/与uniforms开头的/j/发生辅元连读。"},
        {"words": "They cost parents", "phonetic": "/ðeɪ kæst ˈperənts/", "description": "They结尾的/eɪ/与cost开头的/k/发生元辅连读；cost结尾的/t/与parents开头的/p/相邻，发生不完全爆破（失爆）。"},
        {"words": "an average of 337 pounds", "phonetic": "/ən ˈævərɪdʒ əv θri ˈhʌndrəd ən ˈθɜrti ˈsevn paʊndz/", "description": "an结尾的/n/与average开头的/æ/发生辅元连读；average结尾的/dʒ/与of开头的/ə/发生辅元连读；of弱读为/əv/。"},
        {"words": "per year for each", "phonetic": "/pər jɪr fər itʃ/", "description": "per弱读为/pər/；year结尾的/r/与for开头的/f/发生r连读；for弱读为/fər/。"},
        {"words": "secondary school child", "phonetic": "/ˈsekəndəri skul tʃaɪld/", "description": "secondary结尾的/i/与school开头的/s/发生辅元连读；school结尾的/l/与child开头的/tʃ/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Nearly all British schools / have uniforms. / They cost parents / an average of 337 pounds / per year / for each secondary school child.",
        "explanation": "主语(Nearly all British schools)/谓语+宾语(have uniforms)/第二句主谓宾(They cost parents)/直接宾语(an average of 337 pounds)/时间单位(per year)/对象状语(for each secondary school child)，两个句子分别独立，第二个句子按双宾语结构细分。",
    },
}

DATA["According to the new rules, students are required to wear smart black shoes appropriate for the workplace."] = {
    "connected_speech": [
        {"words": "According to the new rules", "phonetic": "/əˈkɔdɪŋ tə ðə nju rulz/", "description": "According结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/；the弱读为/ðə/；new结尾的/u/与rules开头的/r/发生辅元连读。"},
        {"words": "students are required to wear", "phonetic": "/ˈstjudənts ər rɪˈkwaɪrd tə wer/", "description": "students结尾的/s/与are开头的/ɑ/发生辅元连读；are弱读为/ər/；required结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "smart black shoes", "phonetic": "/smɑt blæk ʃuz/", "description": "smart结尾的/t/与black开头的/b/相邻，发生不完全爆破（失爆）；black结尾的/k/与shoes开头的/ʃ/相邻，发生不完全爆破。"},
        {"words": "appropriate for the workplace", "phonetic": "/əˈproʊpriət fər ðə ˈwɜrkpleɪs/", "description": "appropriate结尾的/t/与for开头的/f/发生辅元连读；for弱读为/fər/；the弱读为/ðə/；workplace结尾的/s/可能省略或不发音。"},
    ],
    "sense_groups": {
        "segmented": "According to the new rules, / students are required / to wear smart black shoes / appropriate for the workplace.",
        "explanation": "依据状语(According to the new rules)/主语+谓语(students are required)/主语补足语(to wear smart black shoes)/后置定语(appropriate for the workplace)，逗号后按主-谓-补-定的标准结构展开。",
    },
}

DATA["Harris held that strengthened rules around school uniforms improved student outcomes and behavior."] = {
    "connected_speech": [
        {"words": "Harris held that", "phonetic": "/ˈhærɪs held ðət/", "description": "Harris结尾的/s/与held开头的/h/发生辅元连读；held结尾的/d/与that开头的/ð/相邻，发生不完全爆破（失爆）；that弱读为/ðət/。"},
        {"words": "strengthened rules around", "phonetic": "/ˈstreŋθənd rulz əˈraʊnd/", "description": "strengthened结尾的/d/与rules开头的/r/发生辅元连读；rules结尾的/z/与around开头的/ə/发生辅元连读。"},
        {"words": "school uniforms", "phonetic": "/skul ˈjunɪfɔmz/", "description": "school结尾的/l/与uniforms开头的/j/发生辅音连读。"},
        {"words": "improved student outcomes", "phonetic": "/ɪmˈpruvd ˈstjudənt ˈaʊtkʌmz/", "description": "improved结尾的/d/与student开头的/s/相邻，发生不完全爆破；student结尾的/t/与outcomes开头的/aʊ/发生辅元连读。"},
        {"words": "and behavior", "phonetic": "/ən bɪˈheɪvjər/", "description": "and弱读为/ən/，结尾的/n/与behavior开头的/b/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Harris held / that strengthened rules / around school uniforms / improved student outcomes / and behavior.",
        "explanation": "主句(Harris held)/宾语从句主语(that strengthened rules)/定语(around school uniforms)/宾语从句谓语+宾语1(improved student outcomes)/并列宾语2(and behavior)，按主从关系及从句内部的主-定-谓-宾结构划分。",
    },
}

DATA["As annual inflation climbs over 10%, many households are on tight budgets."] = {
    "connected_speech": [
        {"words": "As annual inflation climbs", "phonetic": "/əz ˈænjuəl ɪnˈfleɪʃən klaɪmz/", "description": "as弱读为/əz/，结尾的/z/与annual开头的/æ/发生辅元连读；annual结尾的/l/与inflation开头的/ɪ/发生辅元连读；inflation结尾的/n/与climbs开头的/k/发生辅元连读。"},
        {"words": "over 10%", "phonetic": "/ˈoʊvər ten pəˈsent/", "description": "over结尾的/r/与10的/t/发生r连读。"},
        {"words": "many households are on", "phonetic": "/ˈmeni ˈhaʊshoʊldz ər ɑn/", "description": "many结尾的/i/与households开头的/h/发生辅元连读；households结尾的/z/与are开头的/ɑ/发生辅元连读；are弱读为/ər/。"},
        {"words": "tight budgets", "phonetic": "/taɪt ˈbʌdʒɪts/", "description": "tight结尾的/t/与budgets开头的/b/相邻，发生不完全爆破（失爆）。"},
    ],
    "sense_groups": {
        "segmented": "As annual inflation / climbs over 10%, / many households / are on tight budgets.",
        "explanation": "时间/原因状语从句主语(As annual inflation)/从句谓语(climbs over 10%)/主句主语(many households)/谓语+表语(are on tight budgets)，按状语从句-主句的结构，逗号分隔自然停顿。",
    },
}

DATA["Private rental prices in Britain rose 3.2% over the 12 months to July 2022, the largest jump since 2016."] = {
    "connected_speech": [
        {"words": "Private rental prices in Britain", "phonetic": "/ˈpraɪvɪt ˈrentəl ˈpraɪsɪz ɪn ˈbrɪtən/", "description": "Private结尾的/t/与rental开头的/r/发生辅元连读；rental结尾的/l/与prices开头的/p/发生辅元连读；prices结尾的/z/与in开头的/ɪ/发生辅元连读；in结尾的/n/与Britain开头的/b/发生辅元连读。"},
        {"words": "rose 3.2%", "phonetic": "/roʊz θri pɔɪnt tu pəˈsent/", "description": "rose结尾的/z/与3.2%开头的/θ/发生辅音连读。"},
        {"words": "over the 12 months", "phonetic": "/ˈoʊvər ðə twelv mʌnθs/", "description": "over结尾的/r/与the的/ðə/发生r连读；twelve结尾的/v/与months开头的/m/发生辅音连读。"},
        {"words": "to July 2022", "phonetic": "/tə dʒuˈlaɪ twenti twenti tu/", "description": "to弱读为/tə/，与July开头的/dʒ/发生辅元连读。"},
        {"words": "the largest jump since 2016", "phonetic": "/ðə ˈlɑdʒɪst dʒʌmp sɪns twenti sɪkˈstin/", "description": "largest结尾的/t/与jump开头的/dʒ/相邻，发生不完全爆破；jump结尾的/p/与since开头的/s/发生辅元连读；since结尾的/s/与2016开头的/t/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Private rental prices in Britain / rose 3.2% / over the 12 months / to July 2022, / the largest jump / since 2016.",
        "explanation": "主语(Private rental prices in Britain)/谓语+幅度(rose 3.2%)/时间范围(over the 12 months)/截止时间(to July 2022)/同位语(the largest jump)/时间状语(since 2016)，按主语-谓语-时间状语-同位补充的信息展开顺序划分。",
    },
}

DATA["Lucinda May, mum of a Taverham student, said she had to ask her parents for 65 pounds to buy her child the correct pair of shoes."] = {
    "connected_speech": [
        {"words": "Lucinda May, mum of a", "phonetic": "/luˈsɪndə meɪ mʌm əv ə/", "description": "May结尾的/eɪ/与mum开头的/m/发生元辅连读；mum结尾的/m/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与a的/ə/发生辅元连读。"},
        {"words": "Taverham student", "phonetic": "/ˈteɪvəhæm ˈstjudənt/", "description": "Taverham结尾的/m/与student开头的/s/发生辅元连读。"},
        {"words": "said she had to ask", "phonetic": "/sed ʃi həd tu æsk/", "description": "said结尾的/d/与she开头的/ʃ/相邻，发生不完全爆破（失爆）；had弱读为/həd/，结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tu/。"},
        {"words": "her parents for 65 pounds", "phonetic": "/hər ˈperənts fər sɪksti faɪv paʊndz/", "description": "her弱读为/hər/；parents结尾的/s/与for开头的/f/发生辅元连读；for弱读为/fər/。"},
        {"words": "to buy her child", "phonetic": "/tə baɪ hər tʃaɪld/", "description": "to弱读为/tə/，与buy开头的/b/发生辅元连读；buy结尾的/aɪ/与her的/hər/发生元辅连读；her弱读为/hər/。"},
        {"words": "the correct pair of shoes", "phonetic": "/ðə kəˈrekt per əv ʃuz/", "description": "correct结尾的/t/与pair开头的/p/相邻，发生不完全爆破；pair结尾的/r/与of开头的/ə/发生r连读；of弱读为/əv/，结尾的/v/与shoes开头的/ʃ/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Lucinda May, / mum of a Taverham student, / said / she had to ask her parents / for 65 pounds / to buy her child / the correct pair of shoes.",
        "explanation": "主语(Lucinda May)/同位语(mum of a Taverham student)/谓语(said)/宾语从句主语+谓语(she had to ask her parents)/金额状语(for 65 pounds)/目的状语(to buy her child)/宾语(the correct pair of shoes)，同位语独立成组，从句内部按动作-金额-目的-宾语的逻辑链展开。",
    },
}

DATA["May said that the school's uniform policy showed the lack of regard for parents dealing with the high cost of living."] = {
    "connected_speech": [
        {"words": "May said that the school's", "phonetic": "/meɪ sed ðət ðə skulz/", "description": "May结尾的/eɪ/与said开头的/s/发生元辅连读；said结尾的/d/与that的/ðət/相邻，发生不完全爆破；that弱读为/ðət/；school's结尾的/z/与uniform开头的/j/发生辅音连读。"},
        {"words": "uniform policy showed", "phonetic": "/ˈjunɪfɔm ˈpɑləsi ʃoʊd/", "description": "uniform结尾的/m/与policy开头的/p/发生辅音连读；policy结尾的/i/与showed开头的/ʃ/发生辅元连读。"},
        {"words": "the lack of regard", "phonetic": "/ðə læk əv rɪˈɡɑd/", "description": "lack结尾的/k/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与regard开头的/r/发生辅音连读。"},
        {"words": "for parents dealing with", "phonetic": "/fər ˈperənts ˈdilɪŋ wɪð/", "description": "for弱读为/fər/；parents结尾的/s/与dealing开头的/d/发生辅元连读；dealing结尾的/ŋ/与with开头的/w/发生辅元连读。"},
        {"words": "the high cost of living", "phonetic": "/ðə haɪ kæst əv ˈlɪvɪŋ/", "description": "high结尾的/aɪ/与cost开头的/k/发生元辅连读；cost结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与living开头的/l/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "May said / that the school's uniform policy / showed / the lack of regard / for parents / dealing with / the high cost of living.",
        "explanation": "主句(May said)/宾语从句主语(that the school's uniform policy)/谓语(showed)/宾语(the lack of regard)/对象状语(for parents)/后置定语(dealing with)/宾语(the high cost of living)，按多层嵌套的从属关系和修饰层次划分。",
    },
}

# ─── cet4-2023-06 ───

DATA["Excuse me, could you tell me where the registration office is?"] = {
    "connected_speech": [
        {"words": "Excuse me", "phonetic": "/ɪkˈskjuz mi/", "description": "Excuse结尾的/z/与me开头的/m/发生辅音连读。"},
        {"words": "could you tell me", "phonetic": "/kʊd ju tel mi/", "description": "could结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与tell开头的/t/发生辅元连读；tell结尾的/l/与me开头的/m/发生辅音连读。"},
        {"words": "where the registration", "phonetic": "/wer ðə ˌredʒɪˈstreɪʃən/", "description": "where结尾的/r/与the的/ðə/发生r连读；the弱读为/ðə/；registration结尾的/n/与office开头的/ɑ/发生辅元连读。"},
        {"words": "office is", "phonetic": "/ˈɑfɪs ɪz/", "description": "office结尾的/s/与is开头的/ɪ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Excuse me, / could you tell me / where the registration office is?",
        "explanation": "礼貌呼语(Excuse me)/主句(could you tell me)/宾语从句(where the registration office is)，按礼貌用语-主句-从句的三层结构划分。",
    },
}

DATA["I'd like to sign up for the psychology course, but it's already full."] = {
    "connected_speech": [
        {"words": "I'd like to sign up", "phonetic": "/aɪd laɪk tə saɪn ʌp/", "description": "I'd结尾的/d/与like开头的/l/相邻，发生不完全爆破（失爆）；like结尾的/k/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/；sign结尾的/n/与up开头的/ʌ/发生辅元连读。"},
        {"words": "for the psychology course", "phonetic": "/fər ðə saɪˈkɑlədʒi kɔs/", "description": "for弱读为/fər/，结尾的/r/与the的/ðə/发生r连读；the弱读为/ðə/；psychology结尾的/i/与course开头的/k/发生辅元连读。"},
        {"words": "but it's already full", "phonetic": "/bət ɪts ɔlˈredi fʊl/", "description": "but结尾的/t/与it's开头的/ɪ/发生辅元连读；it's结尾的/s/与already开头的/ɔ/发生辅元连读；already结尾的/i/与full开头的/f/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "I'd like to sign up / for the psychology course, / but it's already full.",
        "explanation": "主句(I'd like to sign up)/目的状语(for the psychology course)/转折句(but it's already full)，按主从并列的三段式结构划分。",
    },
}

DATA["The library will be closed for renovation during the summer break."] = {
    "connected_speech": [
        {"words": "The library will be closed", "phonetic": "/ðə ˈlaɪbrəri wɪl bi kloʊzd/", "description": "the弱读为/ðə/；library结尾的/i/与will开头的/w/发生辅元连读；will结尾的/l/与be开头的/b/发生辅音连读。"},
        {"words": "for renovation", "phonetic": "/fər ˌrenəˈveɪʃən/", "description": "for弱读为/fər/，结尾的/r/与renovation开头的/r/可合并或轻微延长。"},
        {"words": "during the summer break", "phonetic": "/ˈdjʊrɪŋ ðə ˈsʌmər breɪk/", "description": "during结尾的/ŋ/与the的/ðə/发生辅元连读；summer结尾的/r/与break开头的/b/发生r连读（辅元连读）。"},
    ],
    "sense_groups": {
        "segmented": "The library / will be closed / for renovation / during the summer break.",
        "explanation": "主语(The library)/谓语(will be closed)/原因/目的状语(for renovation)/时间状语(during the summer break)，按主-谓-原因-时间的简洁信息结构划分。",
    },
}

DATA["Students are required to submit their essays by Friday afternoon."] = {
    "connected_speech": [
        {"words": "Students are required to", "phonetic": "/ˈstjudənts ər rɪˈkwaɪrd tə/", "description": "Students结尾的/s/与are开头的/ɑ/发生辅元连读；are弱读为/ər/；required结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "submit their essays", "phonetic": "/səbˈmɪt ðer ˈeseɪz/", "description": "submit结尾的/t/与their开头的/ð/相邻，发生不完全爆破（失爆）；their结尾的/r/与essays开头的/e/发生r连读。"},
        {"words": "by Friday afternoon", "phonetic": "/baɪ ˈfraɪdeɪ ˌɑftəˈnun/", "description": "by结尾的/aɪ/与Friday开头的/f/发生元辅连读；Friday结尾的/eɪ/与afternoon开头的/ɑ/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "Students are required / to submit their essays / by Friday afternoon.",
        "explanation": "主语+谓语(Students are required)/主语补足语(to submit their essays)/时间状语(by Friday afternoon)，按主-谓-补-状的逻辑顺序划分。",
    },
}

DATA["The professor suggested we review Chapter 5 before the exam."] = {
    "connected_speech": [
        {"words": "The professor suggested", "phonetic": "/ðə prəˈfesər səˈdʒestɪd/", "description": "the弱读为/ðə/；professor结尾的/r/与suggested开头的/s/发生r连读（辅元连读）。"},
        {"words": "we review Chapter 5", "phonetic": "/wi rɪˈvju ˈtʃæptər faɪv/", "description": "review结尾的/u/与Chapter开头的/tʃ/发生辅元连读；Chapter结尾的/r/与5的/f/发生r连读。"},
        {"words": "before the exam", "phonetic": "/bɪˈfɔr ði ɪɡˈzæm/", "description": "before结尾的/r/与the的/ði/发生r连读；the在元音前读/ði/，与exam的/ɪ/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "The professor suggested / we review Chapter 5 / before the exam.",
        "explanation": "主句(The professor suggested)/宾语从句(we review Chapter 5)/时间状语(before the exam)，按主从关系和时间逻辑划分。",
    },
}

DATA["Could you recommend a good restaurant near the campus?"] = {
    "connected_speech": [
        {"words": "Could you recommend", "phonetic": "/kʊd ju ˌrekəˈmend/", "description": "could结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与recommend开头的/r/发生辅元连读。"},
        {"words": "a good restaurant", "phonetic": "/ə ɡʊd ˈrestərɑnt/", "description": "a弱读为/ə/，与good开头的/ɡ/发生辅元连读；good结尾的/d/与restaurant开头的/r/相邻，发生不完全爆破。"},
        {"words": "near the campus", "phonetic": "/nɪr ðə ˈkæmpəs/", "description": "near结尾的/r/与the的/ðə/发生r连读；the弱读为/ðə/；campus结尾的/s/可轻微弱化。"},
    ],
    "sense_groups": {
        "segmented": "Could you recommend / a good restaurant / near the campus?",
        "explanation": "疑问助动词+主语+谓语(Could you recommend)/宾语(a good restaurant)/地点状语(near the campus)，按请求-对象-地点的信息顺序划分。",
    },
}

DATA["The bus to the city center runs every fifteen minutes on weekdays."] = {
    "connected_speech": [
        {"words": "The bus to the city center", "phonetic": "/ðə bʌs tə ðə ˈsɪti ˈsentər/", "description": "bus结尾的/s/与to开头的/t/发生辅元连读；to弱读为/tə/；the弱读为/ðə/；city结尾的/i/与center开头的/s/发生辅元连读。"},
        {"words": "runs every fifteen minutes", "phonetic": "/rʌnz ˈevri ˌfɪfˈtin ˈmɪnɪts/", "description": "runs结尾的/z/与every开头的/e/发生辅元连读；every结尾的/i/与fifteen开头的/f/发生辅元连读；fifteen结尾的/n/与minutes开头的/m/发生辅元连读。"},
        {"words": "on weekdays", "phonetic": "/ɑn ˈwikdeɪz/", "description": "on结尾的/n/与weekdays开头的/w/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The bus to the city center / runs / every fifteen minutes / on weekdays.",
        "explanation": "主语+定语(The bus to the city center)/谓语(runs)/频率状语(every fifteen minutes)/时间状语(on weekdays)，按主语-谓语-频率-时间的层次划分。",
    },
}

DATA["I'm having trouble connecting to the university Wi-Fi network."] = {
    "connected_speech": [
        {"words": "I'm having trouble", "phonetic": "/aɪm ˈhævɪŋ ˈtrʌbəl/", "description": "having结尾的/ŋ/与trouble开头的/t/发生辅元连读。"},
        {"words": "connecting to the", "phonetic": "/kəˈnektɪŋ tə ðə/", "description": "connecting结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/；the弱读为/ðə/。"},
        {"words": "university Wi-Fi network", "phonetic": "/ˌjunɪˈvɜrsɪti ˈwaɪfaɪ ˈnetwɜrk/", "description": "university结尾的/i/与Wi-Fi开头的/w/发生辅元连读；Wi-Fi结尾的/aɪ/与network开头的/n/发生元辅连读。"},
    ],
    "sense_groups": {
        "segmented": "I'm having trouble / connecting to / the university Wi-Fi network.",
        "explanation": "主句(I'm having trouble)/补足语(connecting to)/宾语(the university Wi-Fi network)，按主-谓-宾的信息结构简洁划分。",
    },
}

DATA["The deadline for the scholarship application has been extended to next Monday."] = {
    "connected_speech": [
        {"words": "The deadline for the scholarship", "phonetic": "/ðə ˈdedlaɪn fər ðə ˈskɑləʃɪp/", "description": "deadline结尾的/n/与for开头的/f/发生辅元连读；for弱读为/fər/；the弱读为/ðə/。"},
        {"words": "application has been extended", "phonetic": "/ˌæplɪˈkeɪʃən həz bin ɪkˈstendɪd/", "description": "application结尾的/n/与has开头的/h/发生辅元连读；has弱读为/həz/；been结尾的/n/与extended开头的/ɪ/发生辅元连读。"},
        {"words": "to next Monday", "phonetic": "/tə nekst ˈmʌndeɪ/", "description": "to弱读为/tə/，与next开头的/n/发生辅元连读；next结尾的/t/与Monday开头的/m/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "The deadline / for the scholarship application / has been extended / to next Monday.",
        "explanation": "主语(The deadline)/定语(for the scholarship application)/谓语(has been extended)/时间状语(to next Monday)，按主语-定语-谓语-状语的层次划分。",
    },
}

DATA["Would you mind sharing your notes from yesterday's lecture?"] = {
    "connected_speech": [
        {"words": "Would you mind sharing", "phonetic": "/wʊd ju maɪnd ˈʃerɪŋ/", "description": "would结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与mind开头的/m/发生辅元连读；mind结尾的/d/与sharing开头的/ʃ/相邻，发生不完全爆破。"},
        {"words": "your notes from", "phonetic": "/jər noʊts frəm/", "description": "your弱读为/jər/；notes结尾的/s/与from开头的/f/发生辅音连读；from弱读为/frəm/。"},
        {"words": "yesterday's lecture", "phonetic": "/ˈjestədeɪz ˈlektʃər/", "description": "yesterday's结尾的/z/与lecture开头的/l/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Would you mind / sharing your notes / from yesterday's lecture?",
        "explanation": "礼貌请求(Would you mind)/宾语(sharing your notes)/来源状语(from yesterday's lecture)，按请求-动作-来源三部分划分。",
    },
}

# ─── cet4-2023-12 ───

DATA["The company is looking for interns who can work at least three days a week."] = {
    "connected_speech": [
        {"words": "The company is looking for", "phonetic": "/ðə ˈkʌmpəni ɪz ˈlʊkɪŋ fər/", "description": "company结尾的/i/与is开头的/ɪ/发生元元连读；is结尾的/z/与looking开头的/l/发生辅元连读；looking结尾的/ŋ/与for开头的/f/发生辅元连读；for弱读为/fər/。"},
        {"words": "interns who can work", "phonetic": "/ˈɪntɜrnz hu kæn wɜrk/", "description": "interns结尾的/z/与who开头的/h/发生辅元连读；can弱读为/kæn/。"},
        {"words": "at least three days a week", "phonetic": "/ət list θri deɪz ə wik/", "description": "at弱读为/ət/，结尾的/t/与least开头的/l/相邻，发生不完全爆破；least结尾的/t/与three开头的/θ/相邻，发生不完全爆破；days结尾的/z/与a的/ə/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The company / is looking for / interns / who can work / at least three days a week.",
        "explanation": "主语(The company)/谓语(is looking for)/宾语(interns)/定语从句(who can work)/频率状语(at least three days a week)，按主-谓-宾-从句-状语的层次展开。",
    },
}

DATA["We regret to inform you that the position has already been filled."] = {
    "connected_speech": [
        {"words": "We regret to inform you", "phonetic": "/wi rɪˈɡret tu ɪnˈfɔm ju/", "description": "regret结尾的/t/与to开头的/t/相邻，发生不完全爆破；to弱读为/tu/，结尾的/u/与inform开头的/ɪ/发生元元连读；inform结尾的/m/与you开头的/j/发生辅元连读。"},
        {"words": "that the position", "phonetic": "/ðət ðə pəˈzɪʃən/", "description": "that弱读为/ðət/，结尾的/t/与the的/ðə/相邻，发生不完全爆破。"},
        {"words": "has already been filled", "phonetic": "/həz ɔlˈredi bin fɪld/", "description": "has弱读为/həz/，结尾的/z/与already开头的/ɔ/发生辅元连读；already结尾的/i/与been开头的/b/发生辅元连读；been结尾的/n/与filled开头的/f/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "We regret / to inform you / that the position / has already been filled.",
        "explanation": "主句(We regret)/主语补足语(to inform you)/宾语从句主语(that the position)/从句谓语(has already been filled)，按正式书面通知语体的分层结构划分。",
    },
}

DATA["The weather forecast says it's going to rain heavily this afternoon."] = {
    "connected_speech": [
        {"words": "The weather forecast says", "phonetic": "/ðə ˈweðər ˈfɔkæst sez/", "description": "weather结尾的/r/与forecast开头的/f/发生r连读（辅元连读）；forecast结尾的/t/与says开头的/s/相邻，发生不完全爆破。"},
        {"words": "it's going to rain", "phonetic": "/ɪts ˈɡoʊɪŋ tə reɪn/", "description": "it's结尾的/s/与going开头的/ɡ/发生辅音连读；going结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/。"},
        {"words": "heavily this afternoon", "phonetic": "/ˈhevɪli ðɪs ˌɑftəˈnun/", "description": "heavily结尾的/i/与this开头的/ð/发生辅元连读；this结尾的/s/与afternoon开头的/ɑ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The weather forecast says / it's going to rain / heavily / this afternoon.",
        "explanation": "主句(The weather forecast says)/宾语从句主语+谓语(it's going to rain)/程度状语(heavily)/时间状语(this afternoon)，按信息来源-内容-程度-时间的顺序划分。",
    },
}

DATA["I was wondering if you could help me with this math problem."] = {
    "connected_speech": [
        {"words": "I was wondering if you", "phonetic": "/aɪ wəz ˈwʌndərɪŋ ɪf ju/", "description": "was弱读为/wəz/，结尾的/z/与wondering开头的/w/发生辅音连读；wondering结尾的/ŋ/与if开头的/ɪ/发生辅元连读；if结尾的/f/与you开头的/j/发生辅元连读。"},
        {"words": "could help me with", "phonetic": "/kʊd help mi wɪð/", "description": "could结尾的/d/与help开头的/h/相邻，发生不完全爆破；help结尾的/p/与me开头的/m/相邻，发生不完全爆破；me结尾的/i/与with开头的/w/发生辅元连读。"},
        {"words": "this math problem", "phonetic": "/ðɪs mæθ ˈprɑbləm/", "description": "this结尾的/s/与math开头的/m/发生辅音连读；math结尾的/θ/与problem开头的/p/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "I was wondering / if you could help me / with this math problem.",
        "explanation": "礼貌主句(I was wondering)/宾语从句(if you could help me)/状语(with this math problem)，按委婉请求的语法层次划分。",
    },
}

DATA["The museum is free to enter on the first Sunday of every month."] = {
    "connected_speech": [
        {"words": "The museum is free to enter", "phonetic": "/ðə mjuˈziəm ɪz fri tu ˈentər/", "description": "museum结尾的/m/与is开头的/ɪ/发生辅元连读；is结尾的/z/与free开头的/f/发生辅音连读；free结尾的/i/与to的/tu/发生元元连读；to弱读为/tu/；enter结尾的/r/在美式中可与后续元音连读。"},
        {"words": "on the first Sunday", "phonetic": "/ɑn ðə fɜrst ˈsʌndeɪ/", "description": "on结尾的/n/与the的/ðə/发生辅元连读；first结尾的/t/与Sunday开头的/s/相邻，发生不完全爆破。"},
        {"words": "of every month", "phonetic": "/əv ˈevri mʌnθ/", "description": "of弱读为/əv/，结尾的/v/与every开头的/e/发生辅元连读；every结尾的/i/与month开头的/m/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The museum / is free to enter / on the first Sunday / of every month.",
        "explanation": "主语(The museum)/谓语+表语+补语(is free to enter)/时间状语(on the first Sunday)/定语(of every month)，按主-谓-时间的层次划分。",
    },
}

DATA["She decided to take a gap year before starting graduate school."] = {
    "connected_speech": [
        {"words": "She decided to take", "phonetic": "/ʃi dɪˈsaɪdɪd tə teɪk/", "description": "decided结尾的/d/与to开头的/t/相邻，发生不完全爆破（失爆）；to弱读为/tə/；take结尾的/k/与a的/ə/发生辅元连读。"},
        {"words": "a gap year", "phonetic": "/ə ɡæp jɪr/", "description": "gap结尾的/p/与year开头的/j/发生辅元连读。"},
        {"words": "before starting graduate school", "phonetic": "/bɪˈfɔr ˈstɑtɪŋ ˈɡrædʒuət skul/", "description": "before结尾的/r/与starting开头的/s/发生r连读（辅元连读）；starting结尾的/ŋ/与graduate开头的/ɡ/发生辅元连读；graduate结尾的/t/与school开头的/s/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "She decided / to take a gap year / before starting / graduate school.",
        "explanation": "主句(She decided)/不定式宾语(to take a gap year)/时间状语(before starting)/宾语(graduate school)，按决策-行动-时机-目标的逻辑链划分。",
    },
}

DATA["The new shopping mall has attracted a lot of customers since it opened."] = {
    "connected_speech": [
        {"words": "The new shopping mall", "phonetic": "/ðə nju ˈʃɑpɪŋ mɔl/", "description": "new结尾的/u/与shopping开头的/ʃ/发生辅元连读；shopping结尾的/ŋ/与mall开头的/m/发生辅元连读。"},
        {"words": "has attracted a lot of", "phonetic": "/həz əˈtræktɪd ə lɑt əv/", "description": "has弱读为/həz/，结尾的/z/与attracted开头的/ə/发生辅元连读；attracted结尾的/d/与a的/ə/发生辅元连读；lot结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/。"},
        {"words": "customers since it opened", "phonetic": "/ˈkʌstəmərz sɪns ɪt ˈoʊpənd/", "description": "customers结尾的/z/与since开头的/s/相邻，可合并延长；since结尾的/s/与it开头的/ɪ/发生辅元连读；it结尾的/t/与opened开头的/oʊ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The new shopping mall / has attracted / a lot of customers / since it opened.",
        "explanation": "主语(The new shopping mall)/谓语(has attracted)/宾语(a lot of customers)/时间状语从句(since it opened)，按主-谓-宾-状的结构层次划分。",
    },
}

DATA["Please remember to bring your student ID when you come for the interview."] = {
    "connected_speech": [
        {"words": "Please remember to bring", "phonetic": "/pliz rɪˈmembər tə brɪŋ/", "description": "remember结尾的/r/与to开头的/t/发生r连读（辅元连读）；to弱读为/tə/。"},
        {"words": "your student ID", "phonetic": "/jər ˈstjudənt ˌaɪ ˈdi/", "description": "your弱读为/jər/；student结尾的/t/与ID开头的/aɪ/发生辅元连读。"},
        {"words": "when you come for", "phonetic": "/wen ju kʌm fər/", "description": "when结尾的/n/与you开头的/j/发生辅元连读；you结尾的/u/与come开头的/k/发生辅元连读；come结尾的/m/与for开头的/f/发生辅元连读；for弱读为/fər/。"},
        {"words": "the interview", "phonetic": "/ði ˈɪntəvju/", "description": "the在元音前读/ði/，与interview的/ɪ/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "Please remember / to bring your student ID / when you come / for the interview.",
        "explanation": "祈使句主干(Please remember)/不定式宾语(to bring your student ID)/时间状语从句(when you come)/目的状语(for the interview)，按请求-内容-时间-目的的顺序划分。",
    },
}

DATA["The research project has made significant progress in the past few months."] = {
    "connected_speech": [
        {"words": "The research project", "phonetic": "/ðə rɪˈsɜrtʃ ˈprɑdʒekt/", "description": "research结尾的/tʃ/与project开头的/p/发生辅音连读。"},
        {"words": "has made significant progress", "phonetic": "/həz meɪd sɪɡˈnɪfɪkənt ˈproʊɡres/", "description": "has弱读为/həz/，结尾的/z/与made开头的/m/发生辅音连读；made结尾的/d/与significant开头的/s/相邻，发生不完全爆破；significant结尾的/t/与progress开头的/p/相邻，发生不完全爆破。"},
        {"words": "in the past few months", "phonetic": "/ɪn ðə pæst fju mʌnθs/", "description": "past结尾的/t/与few开头的/f/相邻，发生不完全爆破（失爆）；few结尾的/u/与months开头的/m/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The research project / has made / significant progress / in the past few months.",
        "explanation": "主语(The research project)/谓语(has made)/宾语(significant progress)/时间状语(in the past few months)，按主-谓-宾-状的标准结构划分。",
    },
}

DATA["Would you prefer to have the meeting in person or online?"] = {
    "connected_speech": [
        {"words": "Would you prefer to", "phonetic": "/wʊd ju prɪˈfɜrr tə/", "description": "would结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与prefer开头的/p/发生辅元连读；prefer结尾的/r/与to开头的/t/发生r连读；to弱读为/tə/。"},
        {"words": "have the meeting", "phonetic": "/həv ðə ˈmitɪŋ/", "description": "have弱读为/həv/，结尾的/v/与the的/ðə/发生辅元连读；the弱读为/ðə/。"},
        {"words": "in person or online", "phonetic": "/ɪn ˈpɜrsən ɔr ˈɑnlaɪn/", "description": "in结尾的/n/与person开头的/p/发生辅元连读；person结尾的/n/与or开头的/ɔ/发生辅元连读；or结尾的/r/与online开头的/ɑ/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "Would you prefer / to have the meeting / in person / or online?",
        "explanation": "疑问句主干(Would you prefer)/不定式宾语(to have the meeting)/方式状语1(in person)/选择状语(or online)，按选择疑问句的对比结构划分。",
    },
}

# ─── cet4-2024-06 ───

DATA["The train to London will depart from platform 7 in ten minutes."] = {
    "connected_speech": [
        {"words": "The train to London", "phonetic": "/ðə treɪn tə ˈlʌndən/", "description": "train结尾的/n/与to开头的/t/发生辅元连读；to弱读为/tə/，与London开头的/l/发生辅元连读。"},
        {"words": "will depart from platform 7", "phonetic": "/wɪl dɪˈpɑt frəm ˈplætfɔm ˈsevn/", "description": "will结尾的/l/与depart开头的/d/发生辅音连读；depart结尾的/t/与from开头的/f/相邻，发生不完全爆破；from弱读为/frəm/；platform结尾的/m/与7的/s/发生辅元连读。"},
        {"words": "in ten minutes", "phonetic": "/ɪn ten ˈmɪnɪts/", "description": "in结尾的/n/与ten开头的/t/发生辅元连读；ten结尾的/n/与minutes开头的/m/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The train to London / will depart / from platform 7 / in ten minutes.",
        "explanation": "主语+定语(The train to London)/谓语(will depart)/地点状语(from platform 7)/时间状语(in ten minutes)，按主-谓-地点-时间的顺序划分。",
    },
}

DATA["I'd like to exchange this shirt for a larger size, please."] = {
    "connected_speech": [
        {"words": "I'd like to exchange", "phonetic": "/aɪd laɪk tu ɪksˈtʃeɪndʒ/", "description": "I'd结尾的/d/与like开头的/l/相邻，发生不完全爆破；like结尾的/k/与to开头的/t/相邻，发生不完全爆破；to弱读为/tu/，结尾的/u/与exchange开头的/ɪks/发生元辅连读。"},
        {"words": "this shirt for", "phonetic": "/ðɪs ʃɜrt fər/", "description": "this结尾的/s/与shirt开头的/ʃ/可合并或轻微延长；shirt结尾的/t/与for开头的/f/相邻，发生不完全爆破；for弱读为/fər/。"},
        {"words": "a larger size, please", "phonetic": "/ə ˈlɑdʒər saɪz pliz/", "description": "larger结尾的/r/与size开头的/s/发生r连读（辅元连读）；size结尾的/z/与please开头的/p/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "I'd like to exchange / this shirt / for a larger size, / please.",
        "explanation": "主句(I'd like to exchange)/宾语(this shirt)/目的状语(for a larger size)/礼貌词(please)，按请求-对象-目的-礼貌标记的自然语序划分。",
    },
}

DATA["The guest speaker will talk about climate change and its effects on agriculture."] = {
    "connected_speech": [
        {"words": "The guest speaker will talk about", "phonetic": "/ðə ɡest ˈspikər wɪl tɔk əˈbaʊt/", "description": "guest结尾的/t/与speaker开头的/s/相邻，发生不完全爆破；speaker结尾的/r/与will开头的/w/发生r连读；talk结尾的/k/与about开头的/ə/发生辅元连读。"},
        {"words": "climate change and its effects", "phonetic": "/ˈklaɪmət tʃeɪndʒ ən ɪts ɪˈfekts/", "description": "climate结尾的/t/与change开头的/tʃ/相邻，发生不完全爆破；change结尾的/dʒ/与and的/ən/发生辅元连读；and弱读为/ən/；its结尾的/s/与effects开头的/ɪ/发生辅元连读。"},
        {"words": "on agriculture", "phonetic": "/ɑn ˈæɡrɪkʌltʃər/", "description": "on结尾的/n/与agriculture开头的/æ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The guest speaker / will talk about / climate change / and its effects / on agriculture.",
        "explanation": "主语(The guest speaker)/谓语+介词(will talk about)/宾语1(climate change)/并列宾语2(and its effects)/定语(on agriculture)，按主体-动作-并列对象-修饰的逻辑划分。",
    },
}

DATA["Could you give me a wake-up call at six o'clock tomorrow morning?"] = {
    "connected_speech": [
        {"words": "Could you give me", "phonetic": "/kʊd ju ɡɪv mi/", "description": "could结尾的/d/与you开头的/j/发生辅元连读；give结尾的/v/与me开头的/m/发生辅音连读。"},
        {"words": "a wake-up call", "phonetic": "/ə ˈweɪkʌp kɔl/", "description": "wake-up结尾的/p/与call开头的/k/相邻，发生不完全爆破（失爆）。"},
        {"words": "at six o'clock tomorrow morning", "phonetic": "/ət sɪks əˈklɑk təˈmɔroʊ ˈmɔnɪŋ/", "description": "at弱读为/ət/，结尾的/t/与six开头的/s/相邻，发生不完全爆破；six结尾的/s/与o'clock开头的/ə/发生辅元连读；o'clock结尾的/k/与tomorrow开头的/t/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Could you give me / a wake-up call / at six o'clock / tomorrow morning?",
        "explanation": "请求句主干(Could you give me)/宾语(a wake-up call)/具体时间(at six o'clock)/日期说明(tomorrow morning)，按请求-内容-时间的细化顺序划分。",
    },
}

DATA["She's been practicing the piano for at least two hours every day."] = {
    "connected_speech": [
        {"words": "She's been practicing", "phonetic": "/ʃiz bin ˈpræktɪsɪŋ/", "description": "She's结尾的/z/与been开头的/b/发生辅音连读；been结尾的/n/与practicing开头的/p/发生辅元连读。"},
        {"words": "the piano", "phonetic": "/ðə piˈænoʊ/", "description": "the弱读为/ðə/，与piano开头的/p/发生辅元连读。"},
        {"words": "for at least two hours", "phonetic": "/fər ət list tu ˈaʊrz/", "description": "for弱读为/fər/；at弱读为/ət/，结尾的/t/与least开头的/l/相邻，发生不完全爆破；least结尾的/t/与two开头的/t/相邻，发生不完全爆破。"},
        {"words": "every day", "phonetic": "/ˈevri deɪ/", "description": "every结尾的/i/与day开头的/d/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "She's been practicing / the piano / for at least two hours / every day.",
        "explanation": "主语+谓语(She's been practicing)/宾语(the piano)/时长状语(for at least two hours)/频率状语(every day)，按动作-对象-时长-频率的自然描述顺序划分。",
    },
}

DATA["The flight has been delayed due to bad weather conditions at the destination."] = {
    "connected_speech": [
        {"words": "The flight has been delayed", "phonetic": "/ðə flaɪt həz bin dɪˈleɪd/", "description": "flight结尾的/t/与has开头的/h/相邻，发生不完全爆破；has弱读为/həz/，结尾的/z/与been开头的/b/发生辅音连读；been结尾的/n/与delayed开头的/d/发生辅元连读。"},
        {"words": "due to bad weather", "phonetic": "/dju tu bæd ˈweðər/", "description": "due结尾的/u/与to的/tu/发生元元连读；to弱读为/tu/；bad结尾的/d/与weather开头的/w/相邻，发生不完全爆破。"},
        {"words": "conditions at the destination", "phonetic": "/kənˈdɪʃənz ət ðə ˌdestɪˈneɪʃən/", "description": "conditions结尾的/z/与at开头的/ə/发生辅元连读；at弱读为/ət/；the弱读为/ðə/。"},
    ],
    "sense_groups": {
        "segmented": "The flight / has been delayed / due to bad weather conditions / at the destination.",
        "explanation": "主语(The flight)/谓语(has been delayed)/原因状语(due to bad weather conditions)/地点状语(at the destination)，按主-谓-原因-地点的逻辑链划分。",
    },
}

DATA["I'm not sure if I understood the assignment correctly. Could you clarify?"] = {
    "connected_speech": [
        {"words": "I'm not sure if I", "phonetic": "/aɪm nɑt ʃʊr ɪf aɪ/", "description": "not结尾的/t/与sure开头的/ʃ/相邻，发生不完全爆破（失爆）；sure结尾的/r/与if开头的/ɪ/在美式中发生r连读；if结尾的/f/与I开头的/aɪ/发生辅元连读。"},
        {"words": "understood the assignment correctly", "phonetic": "/ˌʌndərˈstʊd ði əˈsaɪnmənt kəˈrektli/", "description": "understood结尾的/d/与the的/ði/相邻，发生不完全爆破；the在元音前读/ði/，与assignment的/ə/发生元元连读。"},
        {"words": "Could you clarify", "phonetic": "/kʊd ju ˈklærɪfaɪ/", "description": "could结尾的/d/与you开头的/j/发生辅元连读；you结尾的/u/与clarify开头的/k/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "I'm not sure / if I understood / the assignment correctly. / Could you clarify?",
        "explanation": "主句(I'm not sure)/宾语从句(if I understood)/宾语(the assignment correctly)/第二句(Could you clarify)，两个句子分属不同话轮，各自独立成组。",
    },
}

DATA["The restaurant serves breakfast from seven to ten in the morning."] = {
    "connected_speech": [
        {"words": "The restaurant serves breakfast", "phonetic": "/ðə ˈrestərɑnt sɜrvz ˈbrekfəst/", "description": "restaurant结尾的/t/与serves开头的/s/相邻，发生不完全爆破；serves结尾的/z/与breakfast开头的/b/发生辅音连读。"},
        {"words": "from seven to ten", "phonetic": "/frəm ˈsevn tə ten/", "description": "from弱读为/frəm/，结尾的/m/与seven开头的/s/发生辅元连读；seven结尾的/n/与to开头的/t/发生辅元连读；to弱读为/tə/，与ten开头的/t/发生辅元连读。"},
        {"words": "in the morning", "phonetic": "/ɪn ðə ˈmɔnɪŋ/", "description": "in结尾的/n/与the的/ðə/发生辅元连读；the弱读为/ðə/。"},
    ],
    "sense_groups": {
        "segmented": "The restaurant / serves breakfast / from seven to ten / in the morning.",
        "explanation": "主语(The restaurant)/谓语+宾语(serves breakfast)/时间范围(from seven to ten)/时段(in the morning)，按主-谓-宾-时间的层次划分。",
    },
}

DATA["He managed to finish the project ahead of schedule despite all the difficulties."] = {
    "connected_speech": [
        {"words": "He managed to finish", "phonetic": "/hi ˈmænɪdʒd tə ˈfɪnɪʃ/", "description": "managed结尾的/d/与to开头的/t/相邻，发生不完全爆破（失爆）；to弱读为/tə/。"},
        {"words": "the project ahead of schedule", "phonetic": "/ðə ˈprɑdʒekt əˈhed əv ˈʃedjul/", "description": "project结尾的/t/与ahead开头的/ə/发生辅元连读；ahead结尾的/d/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与schedule开头的/ʃ/发生辅音连读。"},
        {"words": "despite all the difficulties", "phonetic": "/dɪˈspaɪt ɔl ðə ˈdɪfɪkəltiz/", "description": "despite结尾的/t/与all开头的/ɔ/发生辅元连读；all结尾的/l/与the的/ðə/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "He managed / to finish the project / ahead of schedule / despite all the difficulties.",
        "explanation": "主句(He managed)/不定式宾补(to finish the project)/结果状语(ahead of schedule)/让步状语(despite all the difficulties)，按动作-目标-结果-让步的逻辑层次划分。",
    },
}

DATA["Would it be possible to reschedule our appointment for next Tuesday?"] = {
    "connected_speech": [
        {"words": "Would it be possible", "phonetic": "/wʊd ɪt bi ˈpæsɪbəl/", "description": "would结尾的/d/与it开头的/ɪ/发生辅元连读；it结尾的/t/与be开头的/b/相邻，发生不完全爆破（失爆）。"},
        {"words": "to reschedule our appointment", "phonetic": "/tə ˌriˈʃedjul aʊr əˈpɔɪntmənt/", "description": "to弱读为/tə/，与reschedule开头的/r/发生辅元连读；reschedule结尾的/l/与our的/aʊə/发生辅元连读；our结尾的/r/与appointment开头的/ə/发生r连读。"},
        {"words": "for next Tuesday", "phonetic": "/fər nekst ˈtjuzdeɪ/", "description": "for弱读为/fər/；next结尾的/t/与Tuesday开头的/t/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Would it be possible / to reschedule / our appointment / for next Tuesday?",
        "explanation": "礼貌疑问(Would it be possible)/不定式主语(to reschedule)/宾语(our appointment)/时间状语(for next Tuesday)，按形式主语-真主语-宾语-时间的结构划分。",
    },
}

# ─── cet6-2023-06 ───

DATA["The unprecedented economic growth has brought both opportunities and challenges."] = {
    "connected_speech": [
        {"words": "The unprecedented economic growth", "phonetic": "/ði ʌnˈpresɪdəntɪd ˌikəˈnɑmɪk ɡroʊθ/", "description": "the在元音前读/ði/，与unprecedented的/ʌ/发生元元连读；unprecedented结尾的/d/与economic开头的/i/发生辅元连读；economic结尾的/k/与growth开头的/ɡ/相邻，发生不完全爆破。"},
        {"words": "has brought both", "phonetic": "/həz brɔt boʊθ/", "description": "has弱读为/həz/，结尾的/z/与brought开头的/b/发生辅音连读；brought结尾的/t/与both开头的/b/相邻，发生不完全爆破（失爆）。"},
        {"words": "opportunities and challenges", "phonetic": "/ˌɑpəˈtjunɪtiz ən ˈtʃælɪndʒɪz/", "description": "opportunities结尾的/z/与and的/ən/发生辅元连读；and弱读为/ən/，结尾的/n/与challenges开头的/tʃ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The unprecedented economic growth / has brought / both opportunities / and challenges.",
        "explanation": "主语(The unprecedented economic growth)/谓语(has brought)/宾语1(both opportunities)/并列宾语2(and challenges)，按主-谓-并列宾语的结构层次划分。",
    },
}

DATA["Scientists have discovered a potential link between sleep deprivation and memory loss."] = {
    "connected_speech": [
        {"words": "Scientists have discovered", "phonetic": "/ˈsaɪrntɪsts həv dɪˈskʌvəd/", "description": "Scientists结尾的/s/与have开头的/h/发生辅元连读；have弱读为/həv/，结尾的/v/与discovered开头的/d/发生辅音连读。"},
        {"words": "a potential link", "phonetic": "/ə pəˈtenʃəl lɪŋk/", "description": "a的/ə/与potential开头的/p/发生辅元连读；potential结尾的/l/与link开头的/l/可合并或轻微延长。"},
        {"words": "between sleep deprivation", "phonetic": "/bɪˈtwin slip ˌdeprɪˈveɪʃən/", "description": "between结尾的/n/与sleep开头的/s/发生辅元连读；sleep结尾的/p/与deprivation开头的/d/相邻，发生不完全爆破。"},
        {"words": "and memory loss", "phonetic": "/ən ˈmeməri læs/", "description": "and弱读为/ən/，结尾的/n/与memory开头的/m/发生辅元连读；memory结尾的/i/与loss开头的/l/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Scientists have discovered / a potential link / between sleep deprivation / and memory loss.",
        "explanation": "主语+谓语(Scientists have discovered)/宾语(a potential link)/定语1(between sleep deprivation)/并列定语2(and memory loss)，按科学论断的主-宾-修饰层次划分。",
    },
}

DATA["The government has implemented a series of measures to tackle air pollution."] = {
    "connected_speech": [
        {"words": "The government has implemented", "phonetic": "/ðə ˈɡʌvənmənt həz ˈɪmplɪmentɪd/", "description": "government结尾的/t/与has开头的/h/相邻，发生不完全爆破；has弱读为/həz/，结尾的/z/与implemented开头的/ɪ/发生辅元连读。"},
        {"words": "a series of measures", "phonetic": "/ə ˈsɪriz əv ˈmeʒərz/", "description": "series结尾的/z/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与measures开头的/m/发生辅音连读。"},
        {"words": "to tackle air pollution", "phonetic": "/tə ˈtækəl er pəˈluʃən/", "description": "to弱读为/tə/，与tackle开头的/t/发生辅元连读；tackle结尾的/l/与air开头的/er/发生辅元连读；air结尾的/r/与pollution开头的/p/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "The government / has implemented / a series of measures / to tackle / air pollution.",
        "explanation": "主语(The government)/谓语(has implemented)/宾语(a series of measures)/目的状语(to tackle)/宾语(air pollution)，按主-谓-宾-目的的逻辑层次划分。",
    },
}

DATA["It is essential that we take immediate action to preserve endangered species."] = {
    "connected_speech": [
        {"words": "It is essential that we", "phonetic": "/ɪt ɪz ɪˈsenʃəl ðət wi/", "description": "it结尾的/t/与is开头的/ɪ/发生辅元连读；is结尾的/z/与essential开头的/ɪ/发生辅元连读；essential结尾的/l/与that的/ðət/发生辅音连读；that弱读为/ðət/。"},
        {"words": "take immediate action", "phonetic": "/teɪk ɪˈmidiət ˈækʃən/", "description": "take结尾的/k/与immediate开头的/ɪ/发生辅元连读；immediate结尾的/t/与action开头的/æ/发生辅元连读。"},
        {"words": "to preserve endangered species", "phonetic": "/tə prɪˈzɜrv ɪnˈdeɪndʒəd ˈspiʃiz/", "description": "to弱读为/tə/，与preserve开头的/p/发生辅元连读；preserve结尾的/v/与endangered开头的/ɪ/发生辅元连读；endangered结尾的/d/与species开头的/s/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "It is essential / that we take immediate action / to preserve / endangered species.",
        "explanation": "主句(It is essential)/主语从句(that we take immediate action)/目的状语(to preserve)/宾语(endangered species)，按形式主语句式中从句和目的的逻辑递归划分。",
    },
}

DATA["The professor emphasized the importance of critical thinking in academic research."] = {
    "connected_speech": [
        {"words": "The professor emphasized", "phonetic": "/ðə prəˈfesər ˈemfəsaɪzd/", "description": "professor结尾的/r/与emphasized开头的/e/发生r连读。"},
        {"words": "the importance of critical thinking", "phonetic": "/ði ɪmˈpɔtəns əv ˈkrɪtɪkəl ˈθɪŋkɪŋ/", "description": "the在元音前读/ði/，与importance的/ɪ/发生元元连读；importance结尾的/s/与of开头的/ə/发生辅元连读；of弱读为/əv/；critical结尾的/l/与thinking开头的/θ/发生辅音连读。"},
        {"words": "in academic research", "phonetic": "/ɪn ˌækəˈdemɪk rɪˈsɜrtʃ/", "description": "in结尾的/n/与academic开头的/æ/发生辅元连读；academic结尾的/k/与research开头的/r/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The professor / emphasized / the importance of critical thinking / in academic research.",
        "explanation": "主语(The professor)/谓语(emphasized)/宾语(the importance of critical thinking)/范围状语(in academic research)，按主-谓-宾-状的结构层次划分。",
    },
}

DATA["The advancement of artificial intelligence has revolutionized many industries."] = {
    "connected_speech": [
        {"words": "The advancement of artificial", "phonetic": "/ði ədˈvɑnsmənt əv ˌɑtɪˈfɪʃəl/", "description": "the在元音前读/ði/；advancement结尾的/t/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与artificial开头的/ɑ/发生辅元连读。"},
        {"words": "intelligence has revolutionized", "phonetic": "/ɪnˈtelɪdʒəns həz ˌrevəˈluʃənaɪzd/", "description": "intelligence结尾的/s/与has开头的/h/发生辅元连读；has弱读为/həz/，结尾的/z/与revolutionized开头的/r/发生辅音连读。"},
        {"words": "many industries", "phonetic": "/ˈmeni ˈɪndəstriz/", "description": "many结尾的/i/与industries开头的/ɪ/发生元元连读。"},
    ],
    "sense_groups": {
        "segmented": "The advancement of artificial intelligence / has revolutionized / many industries.",
        "explanation": "主语(The advancement of artificial intelligence)/谓语(has revolutionized)/宾语(many industries)，按主-谓-宾的简洁三层结构划分。",
    },
}

DATA["Many young professionals are choosing to work remotely rather than in traditional offices."] = {
    "connected_speech": [
        {"words": "Many young professionals", "phonetic": "/ˈmeni jʌŋ prəˈfeʃənəlz/", "description": "young结尾的/ŋ/与professionals开头的/p/发生辅元连读。"},
        {"words": "are choosing to work remotely", "phonetic": "/ər ˈtʃuzɪŋ tə wɜrk rɪˈmoʊtli/", "description": "are弱读为/ər/；choosing结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/；work结尾的/k/与remotely开头的/r/发生辅元连读。"},
        {"words": "rather than in traditional offices", "phonetic": "/ˈræðər ðən ɪn trəˈdɪʃənəl ˈɑfɪsɪz/", "description": "rather结尾的/r/与than的/ðən/发生r连读；than弱读为/ðən/；in结尾的/n/与traditional开头的/t/发生辅元连读；traditional结尾的/l/与offices开头的/ɑ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Many young professionals / are choosing / to work remotely / rather than / in traditional offices.",
        "explanation": "主语(Many young professionals)/谓语(are choosing)/宾语(to work remotely)/比较状语(rather than)/比较对象(in traditional offices)，按主-谓-宾-比较结构的逻辑层次划分。",
    },
}

DATA["The documentary highlighted the devastating impact of plastic waste on marine life."] = {
    "connected_speech": [
        {"words": "The documentary highlighted", "phonetic": "/ðə ˌdɑkjuˈmentəri ˈhaɪlaɪtɪd/", "description": "documentary结尾的/i/与highlighted开头的/h/发生辅元连读。"},
        {"words": "the devastating impact", "phonetic": "/ðə ˈdevəsteɪtɪŋ ˈɪmpækt/", "description": "devastating结尾的/ŋ/与impact开头的/ɪ/发生辅元连读。"},
        {"words": "of plastic waste", "phonetic": "/əv ˈplæstɪk weɪst/", "description": "of弱读为/əv/，结尾的/v/与plastic开头的/p/发生辅音连读；plastic结尾的/k/与waste开头的/w/相邻，发生不完全爆破。"},
        {"words": "on marine life", "phonetic": "/ɑn məˈrin laɪf/", "description": "on结尾的/n/与marine开头的/m/发生辅元连读；marine结尾的/n/与life开头的/l/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The documentary / highlighted / the devastating impact / of plastic waste / on marine life.",
        "explanation": "主语(The documentary)/谓语(highlighted)/宾语(the devastating impact)/定语(of plastic waste)/范围状语(on marine life)，按主-谓-宾-定-状的扩展结构划分。",
    },
}

DATA["Effective communication skills are indispensable in today's competitive job market."] = {
    "connected_speech": [
        {"words": "Effective communication skills", "phonetic": "/ɪˈfektɪv kəˌmjunɪˈkeɪʃən skɪlz/", "description": "Effective结尾的/v/与communication开头的/k/发生辅音连读；communication结尾的/n/与skills开头的/s/发生辅元连读。"},
        {"words": "are indispensable", "phonetic": "/ər ˌɪndɪˈspensəbəl/", "description": "are弱读为/ər/，结尾的/r/与indispensable开头的/ɪ/发生r连读。"},
        {"words": "in today's competitive job market", "phonetic": "/ɪn təˈdeɪz kəmˈpetɪtɪv dʒɑb ˈmɑkɪt/", "description": "in结尾的/n/与today's开头的/t/发生辅元连读；today's结尾的/z/与competitive开头的/k/发生辅音连读；competitive结尾的/v/与job开头的/dʒ/发生辅音连读；job结尾的/b/与market开头的/m/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "Effective communication skills / are indispensable / in today's / competitive job market.",
        "explanation": "主语(Effective communication skills)/谓语+表语(are indispensable)/时间修饰(in today's)/范围定语(competitive job market)，按主-谓-时间-范围的信息递进划分。",
    },
}

DATA["The recent survey indicates that public awareness of mental health has increased significantly."] = {
    "connected_speech": [
        {"words": "The recent survey indicates", "phonetic": "/ðə ˈrisənt ˈsɜrveɪ ˈɪndɪkeɪts/", "description": "recent结尾的/t/与survey开头的/s/相邻，发生不完全爆破；survey结尾的/eɪ/与indicates开头的/ɪ/发生元元连读。"},
        {"words": "that public awareness", "phonetic": "/ðət ˈpʌblɪk əˈwernəs/", "description": "that弱读为/ðət/，结尾的/t/与public开头的/p/相邻，发生不完全爆破；public结尾的/k/与awareness开头的/ə/发生辅元连读。"},
        {"words": "of mental health", "phonetic": "/əv ˈmentəl helθ/", "description": "of弱读为/əv/，结尾的/v/与mental开头的/m/发生辅音连读；mental结尾的/l/与health开头的/h/发生辅音连读。"},
        {"words": "has increased significantly", "phonetic": "/həz ɪnˈkrist sɪɡˈnɪfɪkəntli/", "description": "has弱读为/həz/，结尾的/z/与increased开头的/ɪ/发生辅元连读；increased结尾的/t/与significantly开头的/s/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "The recent survey / indicates / that public awareness / of mental health / has increased significantly.",
        "explanation": "主语(The recent survey)/谓语(indicates)/宾语从句主语(that public awareness)/定语(of mental health)/从句谓语+状语(has increased significantly)，按主句-从句嵌套层次划分。",
    },
}

# ─── cet6-2023-12 ───

DATA["The transition to renewable energy sources is crucial for sustainable development."] = {
    "connected_speech": [
        {"words": "The transition to renewable", "phonetic": "/ðə trænˈzɪʃən tə rɪˈnjuəbəl/", "description": "transition结尾的/n/与to开头的/t/发生辅元连读；to弱读为/tə/，结尾的/ə/与renewable开头的/r/发生辅元连读。"},
        {"words": "energy sources is crucial", "phonetic": "/ˈenədʒi ˈsɔsɪz ɪz ˈkruʃəl/", "description": "energy结尾的/i/与sources开头的/s/发生辅元连读；sources结尾的/z/与is开头的/ɪ/发生辅元连读。"},
        {"words": "for sustainable development", "phonetic": "/fər səˈsteɪnəbəl dɪˈveləpmənt/", "description": "for弱读为/fər/，结尾的/r/与sustainable开头的/s/发生r连读；sustainable结尾的/l/与development开头的/d/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "The transition to renewable energy sources / is crucial / for sustainable development.",
        "explanation": "主语(The transition to renewable energy sources)/谓语+表语(is crucial)/目的/范围状语(for sustainable development)，按主-谓-状的层次划分。",
    },
}

DATA["A comprehensive understanding of cultural differences facilitates international collaboration."] = {
    "connected_speech": [
        {"words": "A comprehensive understanding", "phonetic": "/ə ˌkɑmprɪˈhensɪv ˌʌndəˈstændɪŋ/", "description": "comprehensive结尾的/v/与understanding开头的/ʌ/发生辅元连读。"},
        {"words": "of cultural differences", "phonetic": "/əv ˈkʌltʃərəl ˈdɪfrənsɪz/", "description": "of弱读为/əv/，结尾的/v/与cultural开头的/k/发生辅音连读；cultural结尾的/l/与differences开头的/d/发生辅音连读。"},
        {"words": "facilitates international collaboration", "phonetic": "/fəˈsɪlɪteɪts ˌɪntəˈnæʃənəl kəˌlæbəˈreɪʃən/", "description": "facilitates结尾的/s/与international开头的/ɪ/发生辅元连读；international结尾的/l/与collaboration开头的/k/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "A comprehensive understanding / of cultural differences / facilitates / international collaboration.",
        "explanation": "主语(A comprehensive understanding)/定语(of cultural differences)/谓语(facilitates)/宾语(international collaboration)，按主-定-谓-宾的结构划分。",
    },
}

DATA["The committee will evaluate the proposal based on its feasibility and potential impact."] = {
    "connected_speech": [
        {"words": "The committee will evaluate", "phonetic": "/ðə kəˈmɪti wɪl ɪˈvæljueɪt/", "description": "committee结尾的/i/与will开头的/w/发生辅元连读；will结尾的/l/与evaluate开头的/ɪ/发生辅音连读。"},
        {"words": "the proposal based on", "phonetic": "/ðə prəˈpoʊzəl beɪst ɑn/", "description": "proposal结尾的/l/与based开头的/b/发生辅音连读；based结尾的/t/与on开头的/ɑ/发生辅元连读。"},
        {"words": "its feasibility and", "phonetic": "/ɪts ˌfizɪˈbɪlɪti ən/", "description": "its结尾的/s/与feasibility开头的/f/发生辅音连读；feasibility结尾的/i/与and的/ən/发生辅元连读；and弱读为/ən/。"},
        {"words": "potential impact", "phonetic": "/pəˈtenʃəl ˈɪmpækt/", "description": "potential结尾的/l/与impact开头的/ɪ/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "The committee / will evaluate / the proposal / based on its feasibility / and potential impact.",
        "explanation": "主语(The committee)/谓语(will evaluate)/宾语(the proposal)/依据状语(based on its feasibility)/并列依据(and potential impact)，按主-谓-宾-依据的逻辑层次划分。",
    },
}

DATA["Innovation has always been the driving force behind technological breakthroughs."] = {
    "connected_speech": [
        {"words": "Innovation has always been", "phonetic": "/ˌɪnəˈveɪʃən həz ˈɔlweɪz bin/", "description": "Innovation结尾的/n/与has开头的/h/发生辅元连读；has弱读为/həz/，结尾的/z/与always开头的/ɔ/发生辅元连读；always结尾的/z/与been开头的/b/发生辅音连读。"},
        {"words": "the driving force", "phonetic": "/ðə ˈdraɪvɪŋ fɔs/", "description": "driving结尾的/ŋ/与force开头的/f/发生辅元连读。"},
        {"words": "behind technological breakthroughs", "phonetic": "/bɪˈhaɪnd ˌteknəˈlɑdʒɪkəl ˈbreɪkθruz/", "description": "behind结尾的/d/与technological开头的/t/相邻，发生不完全爆破；technological结尾的/l/与breakthroughs开头的/b/发生辅音连读。"},
    ],
    "sense_groups": {
        "segmented": "Innovation / has always been / the driving force / behind technological breakthroughs.",
        "explanation": "主语(Innovation)/谓语(has always been)/表语(the driving force)/定语(behind technological breakthroughs)，按主-谓-表-定的简洁结构划分。",
    },
}

DATA["The percentage of elderly population is projected to double by the year 2050."] = {
    "connected_speech": [
        {"words": "The percentage of elderly population", "phonetic": "/ðə pəˈsentɪdʒ əv ˈeldəli ˌpɑpjuˈleɪʃən/", "description": "percentage结尾的/dʒ/与of开头的/ə/发生辅元连读；of弱读为/əv/，结尾的/v/与elderly开头的/e/发生辅元连读；elderly结尾的/i/与population开头的/p/发生辅元连读。"},
        {"words": "is projected to double", "phonetic": "/ɪz prəˈdʒektɪd tə ˈdʌbəl/", "description": "is结尾的/z/与projected开头的/p/发生辅音连读；projected结尾的/d/与to开头的/t/相邻，发生不完全爆破；to弱读为/tə/。"},
        {"words": "by the year 2050", "phonetic": "/baɪ ðə jɪr twenti ˈfɪfti/", "description": "by结尾的/aɪ/与the的/ðə/发生元辅连读；year结尾的/r/与2050的/t/发生r连读。"},
    ],
    "sense_groups": {
        "segmented": "The percentage of elderly population / is projected / to double / by the year 2050.",
        "explanation": "主语(The percentage of elderly population)/谓语(is projected)/主语补足语(to double)/时间状语(by the year 2050)，按主-谓-补-状的结构划分。",
    },
}

DATA["Reading extensively can significantly enhance your vocabulary and writing proficiency."] = {
    "connected_speech": [
        {"words": "Reading extensively can significantly", "phonetic": "/ˈridɪŋ ɪkˈstensɪvli kæn sɪɡˈnɪfɪkəntli/", "description": "Reading结尾的/ŋ/与extensively开头的/ɪ/发生辅元连读；extensively结尾的/i/与can开头的/k/发生辅元连读；can弱读为/kæn/。"},
        {"words": "enhance your vocabulary", "phonetic": "/ɪnˈhɑns jər vəˈkæbjuləri/", "description": "enhance结尾的/s/与your的/jər/发生辅音连读；your弱读为/jər/。"},
        {"words": "and writing proficiency", "phonetic": "/ən ˈraɪtɪŋ prəˈfɪʃənsi/", "description": "and弱读为/ən/，结尾的/n/与writing开头的/r/发生辅元连读；writing结尾的/ŋ/与proficiency开头的/p/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Reading extensively / can significantly enhance / your vocabulary / and writing proficiency.",
        "explanation": "主语(Reading extensively)/谓语+程度状语(can significantly enhance)/宾语1(your vocabulary)/并列宾语2(and writing proficiency)，按主语-谓语-并列宾语的层次划分。",
    },
}

DATA["The negotiation reached a deadlock as neither party was willing to compromise."] = {
    "connected_speech": [
        {"words": "The negotiation reached", "phonetic": "/ðə nɪˌɡoʊʃiˈeɪʃən ritʃt/", "description": "negotiation结尾的/n/与reached开头的/r/发生辅元连读。"},
        {"words": "a deadlock as neither party", "phonetic": "/ə ˈdedlɑk əz ˈnaɪðər ˈpɑti/", "description": "deadlock结尾的/k/与as开头的/ə/发生辅元连读；as弱读为/əz/；neither结尾的/r/与party开头的/p/发生r连读。"},
        {"words": "was willing to compromise", "phonetic": "/wəz ˈwɪlɪŋ tə ˈkɑmprəmaɪz/", "description": "was弱读为/wəz/，结尾的/z/与willing开头的/w/发生辅音连读；willing结尾的/ŋ/与to开头的/t/发生辅元连读；to弱读为/tə/。"},
    ],
    "sense_groups": {
        "segmented": "The negotiation / reached a deadlock / as neither party / was willing to compromise.",
        "explanation": "主语(The negotiation)/谓语+宾语(reached a deadlock)/原因状语从句主语(as neither party)/从句谓语+宾补(was willing to compromise)，按主句-从句的因果关系层次划分。",
    },
}

DATA["Social media has fundamentally transformed the way people interact with one another."] = {
    "connected_speech": [
        {"words": "Social media has fundamentally", "phonetic": "/ˈsoʊʃəl ˈmidiə həz ˌfʌndəˈmentəli/", "description": "media结尾的/ə/与has开头的/h/发生元辅连读；has弱读为/həz/，结尾的/z/与fundamentally开头的/f/发生辅音连读。"},
        {"words": "transformed the way", "phonetic": "/trænsˈfɔmd ðə weɪ/", "description": "transformed结尾的/d/与the的/ðə/相邻，发生不完全爆破；the弱读为/ðə/。"},
        {"words": "people interact with", "phonetic": "/ˈpipəl ˌɪntərˈækt wɪð/", "description": "people结尾的/l/与interact开头的/ɪ/发生辅元连读；interact结尾的/t/与with开头的/w/相邻，发生不完全爆破。"},
        {"words": "one another", "phonetic": "/wʌn əˈnʌðər/", "description": "one结尾的/n/与another开头的/ə/发生辅元连读。"},
    ],
    "sense_groups": {
        "segmented": "Social media / has fundamentally transformed / the way / people interact / with one another.",
        "explanation": "主语(Social media)/谓语+状语(has fundamentally transformed)/宾语(the way)/定语从句(people interact)/状语(with one another)，按主-谓-宾-从句-状语的层次展开。",
    },
}

DATA["The scholarship is awarded to students who demonstrate exceptional academic performance."] = {
    "connected_speech": [
        {"words": "The scholarship is awarded", "phonetic": "/ðə ˈskɑləʃɪp ɪz əˈwɔdɪd/", "description": "scholarship结尾的/p/与is开头的/ɪ/发生辅元连读；is结尾的/z/与awarded开头的/ə/发生辅元连读。"},
        {"words": "to students who demonstrate", "phonetic": "/tə ˈstjudənts hu ˈdemənstreɪt/", "description": "to弱读为/tə/，与students开头的/s/发生辅元连读；students结尾的/s/与who开头的/h/发生辅元连读；who结尾的/u/与demonstrate开头的/d/发生辅元连读。"},
        {"words": "exceptional academic performance", "phonetic": "/ɪkˈsepʃənəl ˌækəˈdemɪk pəˈfɔməns/", "description": "exceptional结尾的/l/与academic开头的/æ/发生辅元连读；academic结尾的/k/与performance开头的/p/相邻，发生不完全爆破。"},
    ],
    "sense_groups": {
        "segmented": "The scholarship / is awarded / to students / who demonstrate / exceptional academic performance.",
        "explanation": "主语(The scholarship)/谓语(is awarded)/对象状语(to students)/定语从句(who demonstrate)/从句宾语(exceptional academic performance)，按主-谓-对象-从句的结构层次划分。",
    },
}

DATA["Addressing income inequality requires coordinated efforts from both government and society."] = {
    "connected_speech": [
        {"words": "Addressing income inequality", "phonetic": "/əˈdresɪŋ ˈɪnkʌm ˌɪnɪˈkwɑlɪti/", "description": "Addressing结尾的/ŋ/与income开头的/ɪ/发生辅元连读；income结尾的/m/与inequality开头的/ɪ/发生辅元连读。"},
        {"words": "requires coordinated efforts", "phonetic": "/rɪˈkwaɪrz koʊˈɔdɪneɪtɪd ˈefəts/", "description": "requires结尾的/z/与coordinated开头的/k/发生辅音连读；coordinated结尾的/d/与efforts开头的/e/发生辅元连读。"},
        {"words": "from both government and society", "phonetic": "/frəm boʊθ ˈɡʌvənmənt ən səˈsaɪrti/", "description": "from弱读为/frəm/，结尾的/m/与both开头的/b/发生辅元连读；both结尾的/θ/与government开头的/ɡ/发生辅音连读；government结尾的/t/与and的/ən/发生辅元连读；and弱读为/ən/。"},
    ],
    "sense_groups": {
        "segmented": "Addressing income inequality / requires / coordinated efforts / from both government / and society.",
        "explanation": "主语(Addressing income inequality)/谓语(requires)/宾语(coordinated efforts)/来源状语(from both government)/并列来源(and society)，按主-谓-宾-来源的层次划分。",
    },
}


async def main():
    db = await get_db()
    try:
        async with db.cursor() as cur:
            # Clear existing data
            await cur.execute("DELETE FROM listening_sentence_analysis")
            print("Cleared existing analysis data.")

            inserted = 0
            skipped = 0
            for text, analysis in DATA.items():
                try:
                    cs_json = json.dumps(analysis["connected_speech"], ensure_ascii=False)
                    await cur.execute(
                        "INSERT INTO listening_sentence_analysis (sentence_text, connected_speech, sense_groups_segmented, sense_groups_explanation) VALUES (%s, %s, %s, %s)",
                        (
                            text,
                            cs_json,
                            analysis["sense_groups"]["segmented"],
                            analysis["sense_groups"]["explanation"],
                        ),
                    )
                    inserted += 1
                except Exception as e:
                    print(f"  ERROR: {text[:60]}... -> {e}")
                    skipped += 1

            await db.commit()
            print(f"Inserted {inserted} records, skipped {skipped}.")
    finally:
        await release_db(db)


if __name__ == "__main__":
    asyncio.run(main())
