from db import get_db, release_db

# ── 5 套原有真题 (从 listeningData.ts 迁移，无 section 结构) ──

OLD_SETS = [
    {
        "id": "cet4-2023-06",
        "name": "2023年6月 CET-4 真题",
        "type": "cet4",
        "year": 2023,
        "month": 6,
        "sentences": [
            ("Excuse me, could you tell me where the registration office is?", "打扰一下，请问注册办公室在哪里？"),
            ("I'd like to sign up for the psychology course, but it's already full.", "我想报名心理学课程，但已经满了。"),
            ("The library will be closed for renovation during the summer break.", "图书馆将在暑假期间关闭进行翻修。"),
            ("Students are required to submit their essays by Friday afternoon.", "学生必须在周五下午之前提交论文。"),
            ("The professor suggested we review Chapter 5 before the exam.", "教授建议我们在考试前复习第五章。"),
            ("Could you recommend a good restaurant near the campus?", "你能推荐学校附近一家好的餐厅吗？"),
            ("The bus to the city center runs every fifteen minutes on weekdays.", "去市中心的公交车工作日每十五分钟一班。"),
            ("I'm having trouble connecting to the university Wi-Fi network.", "我连接大学Wi-Fi网络时遇到问题。"),
            ("The deadline for the scholarship application has been extended to next Monday.", "奖学金申请的截止日期已延长到下周一。"),
            ("Would you mind sharing your notes from yesterday's lecture?", "你介意分享昨天讲座的笔记吗？"),
        ],
    },
    {
        "id": "cet4-2023-12",
        "name": "2023年12月 CET-4 真题",
        "type": "cet4",
        "year": 2023,
        "month": 12,
        "sentences": [
            ("The company is looking for interns who can work at least three days a week.", "公司正在寻找每周至少能工作三天的实习生。"),
            ("We regret to inform you that the position has already been filled.", "我们很遗憾地通知您，该职位已经招满。"),
            ("The weather forecast says it's going to rain heavily this afternoon.", "天气预报说今天下午会有大雨。"),
            ("I was wondering if you could help me with this math problem.", "我想知道你能不能帮我解决这道数学题。"),
            ("The museum is free to enter on the first Sunday of every month.", "博物馆每月的第一个周日免费入场。"),
            ("She decided to take a gap year before starting graduate school.", "她决定在开始研究生学习前休一个间隔年。"),
            ("The new shopping mall has attracted a lot of customers since it opened.", "新购物中心自开业以来吸引了很多顾客。"),
            ("Please remember to bring your student ID when you come for the interview.", "请记得来面试时带上你的学生证。"),
            ("The research project has made significant progress in the past few months.", "该研究项目在过去几个月取得了重大进展。"),
            ("Would you prefer to have the meeting in person or online?", "你更希望面对面开会还是线上开会？"),
        ],
    },
    {
        "id": "cet4-2024-06",
        "name": "2024年6月 CET-4 真题",
        "type": "cet4",
        "year": 2024,
        "month": 6,
        "sentences": [
            ("The train to London will depart from platform 7 in ten minutes.", "开往伦敦的火车将在十分钟后从7号站台出发。"),
            ("I'd like to exchange this shirt for a larger size, please.", "我想把这件衬衫换大一号。"),
            ("The guest speaker will talk about climate change and its effects on agriculture.", "嘉宾演讲者将讨论气候变化及其对农业的影响。"),
            ("Could you give me a wake-up call at six o'clock tomorrow morning?", "明天早上六点能给我一个叫醒电话吗？"),
            ("She's been practicing the piano for at least two hours every day.", "她每天至少练习钢琴两个小时。"),
            ("The flight has been delayed due to bad weather conditions at the destination.", "由于目的地天气状况不佳，航班已延误。"),
            ("I'm not sure if I understood the assignment correctly. Could you clarify?", "我不确定是否正确理解了作业要求。你能说明一下吗？"),
            ("The restaurant serves breakfast from seven to ten in the morning.", "餐厅早上七点到十点供应早餐。"),
            ("He managed to finish the project ahead of schedule despite all the difficulties.", "尽管困难重重，他还是提前完成了项目。"),
            ("Would it be possible to reschedule our appointment for next Tuesday?", "能把我们的预约改到下周二吗？"),
        ],
    },
    {
        "id": "cet6-2023-06",
        "name": "2023年6月 CET-6 真题",
        "type": "cet6",
        "year": 2023,
        "month": 6,
        "sentences": [
            ("The unprecedented economic growth has brought both opportunities and challenges.", "前所未有的经济增长既带来了机遇也带来了挑战。"),
            ("Scientists have discovered a potential link between sleep deprivation and memory loss.", "科学家发现了睡眠不足与记忆力衰退之间的潜在联系。"),
            ("The government has implemented a series of measures to tackle air pollution.", "政府已实施一系列措施来应对空气污染。"),
            ("It is essential that we take immediate action to preserve endangered species.", "我们必须立即采取行动保护濒危物种。"),
            ("The professor emphasized the importance of critical thinking in academic research.", "教授强调了批判性思维在学术研究中的重要性。"),
            ("The advancement of artificial intelligence has revolutionized many industries.", "人工智能的进步已彻底改变了许多行业。"),
            ("Many young professionals are choosing to work remotely rather than in traditional offices.", "许多年轻职业人士选择远程工作而非传统办公室。"),
            ("The documentary highlighted the devastating impact of plastic waste on marine life.", "这部纪录片突出了塑料垃圾对海洋生物的毁灭性影响。"),
            ("Effective communication skills are indispensable in today's competitive job market.", "有效的沟通技巧在当今竞争激烈的就业市场中不可或缺。"),
            ("The recent survey indicates that public awareness of mental health has increased significantly.", "最近的调查表明公众对心理健康的意识已显著提高。"),
        ],
    },
    {
        "id": "cet6-2023-12",
        "name": "2023年12月 CET-6 真题",
        "type": "cet6",
        "year": 2023,
        "month": 12,
        "sentences": [
            ("The transition to renewable energy sources is crucial for sustainable development.", "向可再生能源的过渡对可持续发展至关重要。"),
            ("A comprehensive understanding of cultural differences facilitates international collaboration.", "对文化差异的全面理解有助于国际合作。"),
            ("The committee will evaluate the proposal based on its feasibility and potential impact.", "委员会将根据可行性和潜在影响评估该提案。"),
            ("Innovation has always been the driving force behind technological breakthroughs.", "创新一直是技术突破背后的驱动力。"),
            ("The percentage of elderly population is projected to double by the year 2050.", "预计到2050年老年人口比例将翻倍。"),
            ("Reading extensively can significantly enhance your vocabulary and writing proficiency.", "广泛阅读可以显著提高词汇量和写作能力。"),
            ("The negotiation reached a deadlock as neither party was willing to compromise.", "由于双方都不愿妥协，谈判陷入了僵局。"),
            ("Social media has fundamentally transformed the way people interact with one another.", "社交媒体从根本上改变了人们相互交流的方式。"),
            ("The scholarship is awarded to students who demonstrate exceptional academic performance.", "该奖学金颁发给学业表现优异的学生。"),
            ("Addressing income inequality requires coordinated efforts from both government and society.", "解决收入不平等问题需要政府和社会的共同努力。"),
        ],
    },
]

# ── 2025年12月 CET-4 真题（第一套） ──

NEW_SET = {
    "id": "cet4-2025-12",
    "name": "2025年12月 CET-4 真题（第一套）",
    "type": "cet4",
    "year": 2025,
    "month": 12,
    "sections": [
        {
            "id": "cet4-2025-12-secA",
            "name": "Section A: News Reports",
            "section_type": "news_report",
            "sort_order": 0,
            "sentences": [
                ("A terrified cat has survived a five-mile round trip under the engine cover of a car on a school run.", "一只受惊的猫在汽车引擎盖下经历了一次五英里的往返行程后幸存了下来。"),
                ("The black cat was found curled up under the engine cover of David King's car when he decided to do an oil check after dropping his grandson off at school.", "这只黑猫被发现蜷缩在David King的汽车引擎盖下，当时他在送完孙子上学后决定检查机油。"),
                ("We weren't even sure it was alive, so I gently pushed it with a stick to check it was breathing and saw it was a terrified little cat.", "我们甚至不确定它还活着，所以我用棍子轻轻推了推它，看它是否还在呼吸，发现是只受惊的小猫。"),
                ("Following a rescue by UK charity Cats Protection, the four year old cat was later reunited with its owner, Mr King's neighbour.", "在英國慈善机构猫咪保护组织的救助下，这只四岁的猫后来与它的主人——King先生的邻居团聚了。"),
                ("In less than a month, the Special Olympics Spring Games will make a return to Fayetteville for the first time in five years.", "在不到一个月的时间里，特奥会春季运动会将五年来首次重返费耶特维尔。"),
                ("Event organizer Benjamin Koalzick says he's excited that athletes will get a chance to come back and demonstrate their abilities.", "活动组织者Benjamin Koalzick表示，他很兴奋运动员们将有机会回来展示他们的能力。"),
                ("Organizers expect about one hundred athletes will come out to compete in a variety of events including running, throwing, and jumping.", "组织者预计约有一百名运动员将参加包括跑步、投掷和跳跃在内的各种项目比赛。"),
                ("Kawalski said it's rewarding to see athletes with special needs triumph in the games.", "Kawalski说，看到有特殊需求的运动员在比赛中获胜是很有成就感的。"),
                ("A German supermarket has been ordered to destroy its chocolate rabbits after losing a court battle with a Swiss chocolate manufacturer.", "一家德国超市在与瑞士巧克力制造商的官司败诉后，被勒令销毁其巧克力兔子。"),
                ("The Swiss firm had argued its gold wrapped chocolate rabbit deserved copyright protection from a similar product sold by the budget supermarket.", "瑞士公司主张其金色包装的巧克力兔子应受到版权保护，免受廉价超市销售的类似产品侵害。"),
                ("Switzerland's highest court agreed and overturned a ruling last year that had sided with the supermarket.", "瑞士最高法院同意了这一主张，并推翻了去年支持超市的裁决。"),
                ("The court suggested the chocolate needn't be wasted; it could be melted for use in other products.", "法院建议巧克力不必浪费，可以融化用于其他产品。"),
                ("The Swiss manufacturer's rabbit has a red bow and bell, while the German supermarket's has a green bow and bell.", "瑞士制造商的兔子有红色蝴蝶结和铃铛，而德国超市的兔子是绿色蝴蝶结和铃铛。"),
            ],
        },
        {
            "id": "cet4-2025-12-secB",
            "name": "Section B: Long Conversations",
            "section_type": "long_conversation",
            "sort_order": 1,
            "sentences": [
                ("Can you please hand me that book over there? It has instructions for making a winter bean salad.", "你能把那本书递给我吗？上面有做冬季豆子沙拉的说明。"),
                ("My sister's boyfriend is coming over for dinner. He's vegetarian, so I need to make a lot of vegetable dishes.", "我姐姐的男朋友要来吃晚饭。他是素食主义者，所以我需要做很多蔬菜菜肴。"),
                ("He only eats vegetables, no meat. That doesn't sound like a very balanced diet.", "他只吃蔬菜不吃肉。这听起来不太均衡的饮食。"),
                ("How can he get enough protein? What does he do to strengthen his muscles and all that?", "他怎么获得足够的蛋白质？他怎么增强肌肉什么的？"),
                ("Apparently that's no problem. He eats a variety of different vegetables and nuts, especially those with high amounts of protein.", "显然这没问题。他吃各种不同的蔬菜和坚果，尤其是那些蛋白质含量高的。"),
                ("He's an animal activist. He's always been very sensitive and sympathizes with animals.", "他是一个动物权益活动者。他一直非常敏感并同情动物。"),
                ("He says that keeping animals in zoos and parks causes them great distress.", "他说把动物关在动物园和公园里会给它们带来巨大的痛苦。"),
                ("Not all zoos and animal parks have the most favorable conditions, but without them it just wouldn't be feasible to learn about animals.", "并非所有动物园和动物公园都有最有利的条件，但没有它们就不可能了解动物。"),
                ("I don't think I could ever give up a good hot dog at a baseball game.", "我觉得我永远无法在棒球比赛中放弃一个美味的热狗。"),
                ("Did you see that television program on air travel last night?", "你昨晚看了那个关于航空旅行的电视节目吗？"),
                ("I was surprised that the expert recommended not eating for the entire journey and avoiding sleeping on the plane.", "我很惊讶专家建议整个旅程不吃东西，并避免在飞机上睡觉。"),
                ("I read an article on the subject in the past that suggested the opposite — that it was important not to miss meals.", "我过去读过一篇关于这个话题的文章，建议恰恰相反——不要错过餐食很重要。"),
                ("Well, the expert on the show did cite research supporting her recommendations, so I guess I'll give it a try next time.", "节目中的专家确实引用了支持她建议的研究，所以我想下次我会试试。"),
                ("Jet lag is a big problem for me and has been for the last few years even though I never suffered from it before.", "时差对我来说是个大问题，过去几年一直如此，尽管我以前从不受时差困扰。"),
                ("She did say that jet lag often becomes more of a problem after 40, so I guess I'm lucky that I can still adjust.", "她确实说过时差通常在40岁以后变得更严重，所以我想我很幸运还能适应。"),
                ("Actually, my mother is terrified of airplanes to the point where she can't even fly, so our family vacations were always by car or train.", "事实上，我妈妈非常害怕飞机，以至于她根本不能坐飞机，所以我们家的度假总是开车或坐火车。"),
                ("I just get anxious before I fly and feel nervous the whole time we're in the air.", "我只是在飞行前感到焦虑，在空中一直都紧张。"),
                ("The expert said 20% of people are afraid to fly, but actually it was a quarter of people, so the problem really is widespread.", "专家说20%的人害怕飞行，但实际上有四分之一的人害怕，所以这个问题确实很普遍。"),
            ],
        },
        {
            "id": "cet4-2025-12-secC",
            "name": "Section C: Passages",
            "section_type": "passage",
            "sort_order": 2,
            "sentences": [
                ("Nothing can substitute real world experience when it comes to getting started in user experience design.", "在用户体验设计入门方面，没有什么能替代真实世界的经验。"),
                ("Higher education is a great way to equip yourself with some core skills, but it will not prepare you for actual challenges with clients.", "高等教育是装备自己核心技能的好方法，但它不会让你为面对客户的实际挑战做好准备。"),
                ("Being proficient with a design tool and a few methods doesn't make you a user experience designer.", "熟练使用设计工具和一些方法并不代表你就是一个用户体验设计师。"),
                ("There simply isn't a one size fits all process. Being effective requires adaptability, something you don't really learn in school.", "根本不存在一刀切的流程。要有效就需要适应性，而这在学校是学不到的。"),
                ("I found my way to user experience through graphic design and slowly over many different roles and experiences.", "我通过平面设计找到了通往用户体验的道路，并在许多不同的角色和经历中慢慢成长。"),
                ("It took time and commitment to continue to pursue roles within teams that I knew could teach and challenge me.", "这需要时间和投入，继续在那些我知道能教导和挑战我的团队中追求角色。"),
                ("You can start anywhere as long as you know your end goal and you commit to actively pursue opportunities to learn and grow.", "只要你知道自己的最终目标，并致力于积极追求学习和成长的机会，你可以从任何地方开始。"),
                ("When planning for this year, our principal asked what needed to change to engage students more in their learning.", "在今年做规划时，我们的校长问需要改变什么才能让学生更多地参与学习。"),
                ("I responded in a whisper: flexible seating, thinking about our classroom with rows of desks and name plates.", "我低声回答：灵活座位，想着我们那有着一排排课桌和姓名牌的教室。"),
                ("Flexible seating has been defined as movable furniture to create an engaging learning environment.", "灵活座位被定义为可移动的家具，以创造有吸引力的学习环境。"),
                ("It is a shift in practice from being teacher focused to student focused learning.", "这是从以教师为中心向以学生为中心学习的实践转变。"),
                ("For us, flexible seating has meant removing most of the traditional chairs and desks and introducing a variety of seating options.", "对我们来说，灵活座位意味着移除大部分传统桌椅，引入各种座位选择。"),
                ("Teachers tend to still use the rows format because of either the need to control students or the belief that the teacher is the most important person.", "教师仍然倾向于使用排排坐的形式，要么是因为需要控制学生，要么是认为教师是最重要的人。"),
                ("Flexible seating enhances student ownership of space and engagement in learning while reducing rates of disengagement.", "灵活座位增强了学生对空间的主人翁感和学习参与度，同时降低了脱离学习的情况。"),
                ("Dozens of British students arriving for their first day of school on Tuesday were sent home over their shoes.", "数十名英国学生周二第一天上学因鞋子问题被送回家。"),
                ("About 30 students were turned away from Taverham high school in Norfolk due to a change in the school's uniform policy.", "由于学校制服政策的变更，诺福克郡Taverham高中有约30名学生被拒之门外。"),
                ("The head teacher said he notified parents of the updated rules in an email in June.", "校长说他六月份通过电子邮件通知了家长们更新后的规定。"),
                ("The price of school uniforms can spark panic among families struggling with the high cost of living.", "校服的价格可能在生活成本高涨中挣扎的家庭中引发恐慌。"),
                ("Nearly all British schools have uniforms. They cost parents an average of 337 pounds per year for each secondary school child.", "几乎所有的英国学校都有校服。每个中学生的校服平均每年花费家长337英镑。"),
                ("According to the new rules, students are required to wear smart black shoes appropriate for the workplace.", "根据新规定，学生需穿着适合工作场所的黑色正装皮鞋。"),
                ("Harris held that strengthened rules around school uniforms improved student outcomes and behavior.", "Harris认为加强校服规定改善了学生的成绩和行为。"),
                ("As annual inflation climbs over 10%, many households are on tight budgets.", "随着年通胀率攀升超过10%，许多家庭预算紧张。"),
                ("Private rental prices in Britain rose 3.2% over the 12 months to July 2022, the largest jump since 2016.", "截至2022年7月的12个月内，英国私人租金上涨了3.2%，这是自2016年以来的最大涨幅。"),
                ("Lucinda May, mum of a Taverham student, said she had to ask her parents for 65 pounds to buy her child the correct pair of shoes.", "Taverham学生家长Lucinda May说，她不得不向父母要65英镑给孩子买一双符合规定的鞋子。"),
                ("May said that the school's uniform policy showed the lack of regard for parents dealing with the high cost of living.", "May说学校的制服政策表明了对应对高生活成本家长缺乏体谅。"),
            ],
        },
    ],
}


async def seed_listening_data() -> None:
    db = await get_db()
    try:
        async with db.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM listening_set")
            row = await cur.fetchone()
            if row and row[0] > 0:
                return

        all_sets = list(OLD_SETS)

        for s in all_sets:
            async with db.cursor() as cur:
                await cur.execute(
                    "INSERT INTO listening_set(id, name, type, year, month, set_order) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                    (s["id"], s["name"], s["type"], s["year"], s["month"], 0),
                )
                for i, (en, zh) in enumerate(s["sentences"]):
                    await cur.execute(
                        "INSERT INTO listening_sentence(id, set_id, section_id, en, zh, sort_order) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE en=VALUES(en), zh=VALUES(zh)",
                        (f"{s['id']}-s{i+1}", s["id"], None, en, zh, i),
                    )

        ns = NEW_SET
        async with db.cursor() as cur:
            await cur.execute(
                "INSERT INTO listening_set(id, name, type, year, month, set_order) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                (ns["id"], ns["name"], ns["type"], ns["year"], ns["month"], 1),
            )
        for sec in ns["sections"]:
            async with db.cursor() as cur:
                await cur.execute(
                    "INSERT INTO listening_section(id, set_id, name, section_type, sort_order) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                    (sec["id"], ns["id"], sec["name"], sec["section_type"], sec["sort_order"]),
                )
                for i, (en, zh) in enumerate(sec["sentences"]):
                    await cur.execute(
                        "INSERT INTO listening_sentence(id, set_id, section_id, en, zh, sort_order) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE en=VALUES(en), zh=VALUES(zh)",
                        (f"{sec['id']}-s{i+1}", ns["id"], sec["id"], en, zh, i),
                    )

        await db.commit()
    finally:
        await release_db(db)
