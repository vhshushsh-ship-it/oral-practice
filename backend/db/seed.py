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
            "items": [
                {
                    "id": "cet4-2025-12-itemA1",
                    "name": "News Report One",
                    "sort_order": 0,
                    "sentences": [
                        ("A terrified cat has survived a five-mile round trip under the engine cover of a car on a school run.", "一只受惊的猫在汽车引擎盖下经历了一次五英里的往返行程后幸存了下来。"),
                        ("The black cat was found curled up under the engine cover of David King's car when he decided to do an oil check after dropping his grandson off at school.", "这只黑猫被发现蜷缩在David King的汽车引擎盖下，当时他在送完孙子上学后决定检查机油。"),
                        ("We weren't even sure it was alive, so I gently pushed it with a stick to check it was breathing and saw it was a terrified little cat.", "我们甚至不确定它还活着，所以我用棍子轻轻推了推它，看它是否还在呼吸，发现是只受惊的小猫。"),
                        ("Following a rescue by UK charity Cats Protection, the four year old cat was later reunited with its owner, Mr King's neighbour.", "在英國慈善机构猫咪保护组织的救助下，这只四岁的猫后来与它的主人——King先生的邻居团聚了。"),
                    ],
                },
                {
                    "id": "cet4-2025-12-itemA2",
                    "name": "News Report Two",
                    "sort_order": 1,
                    "sentences": [
                        ("In less than a month, the Special Olympics Spring Games will make a return to Fayetteville for the first time in five years.", "在不到一个月的时间里，特奥会春季运动会将五年来首次重返费耶特维尔。"),
                        ("Event organizer Benjamin Koalzick says he's excited that athletes will get a chance to come back and demonstrate their abilities.", "活动组织者Benjamin Koalzick表示，他很兴奋运动员们将有机会回来展示他们的能力。"),
                        ("Organizers expect about one hundred athletes will come out to compete in a variety of events including running, throwing, and jumping.", "组织者预计约有一百名运动员将参加包括跑步、投掷和跳跃在内的各种项目比赛。"),
                        ("Kawalski said it's rewarding to see athletes with special needs triumph in the games.", "Kawalski说，看到有特殊需求的运动员在比赛中获胜是很有成就感的。"),
                    ],
                },
                {
                    "id": "cet4-2025-12-itemA3",
                    "name": "News Report Three",
                    "sort_order": 2,
                    "sentences": [
                        ("A German supermarket has been ordered to destroy its chocolate rabbits after losing a court battle with a Swiss chocolate manufacturer.", "一家德国超市在与瑞士巧克力制造商的官司败诉后，被勒令销毁其巧克力兔子。"),
                        ("The Swiss firm had argued its gold wrapped chocolate rabbit deserved copyright protection from a similar product sold by the budget supermarket.", "瑞士公司主张其金色包装的巧克力兔子应受到版权保护，免受廉价超市销售的类似产品侵害。"),
                        ("Switzerland's highest court agreed and overturned a ruling last year that had sided with the supermarket.", "瑞士最高法院同意了这一主张，并推翻了去年支持超市的裁决。"),
                        ("The court suggested the chocolate needn't be wasted; it could be melted for use in other products.", "法院建议巧克力不必浪费，可以融化用于其他产品。"),
                        ("The Swiss manufacturer's rabbit has a red bow and bell, while the German supermarket's has a green bow and bell.", "瑞士制造商的兔子有红色蝴蝶结和铃铛，而德国超市的兔子是绿色蝴蝶结和铃铛。"),
                    ],
                },
            ],
        },
        {
            "id": "cet4-2025-12-secB",
            "name": "Section B: Long Conversations",
            "section_type": "long_conversation",
            "sort_order": 1,
            "items": [
                {
                    "id": "cet4-2025-12-itemB1",
                    "name": "Conversation One",
                    "sort_order": 0,
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
                    ],
                },
                {
                    "id": "cet4-2025-12-itemB2",
                    "name": "Conversation Two",
                    "sort_order": 1,
                    "sentences": [
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
            ],
        },
        {
            "id": "cet4-2025-12-secC",
            "name": "Section C: Passages",
            "section_type": "passage",
            "sort_order": 2,
            "items": [
                {
                    "id": "cet4-2025-12-itemC1",
                    "name": "Passage One",
                    "sort_order": 0,
                    "sentences": [
                        ("Nothing can substitute real world experience when it comes to getting started in user experience design.", "在用户体验设计入门方面，没有什么能替代真实世界的经验。"),
                        ("Higher education is a great way to equip yourself with some core skills, but it will not prepare you for actual challenges with clients.", "高等教育是装备自己核心技能的好方法，但它不会让你为面对客户的实际挑战做好准备。"),
                        ("Being proficient with a design tool and a few methods doesn't make you a user experience designer.", "熟练使用设计工具和一些方法并不代表你就是一个用户体验设计师。"),
                        ("There simply isn't a one size fits all process. Being effective requires adaptability, something you don't really learn in school.", "根本不存在一刀切的流程。要有效就需要适应性，而这在学校是学不到的。"),
                        ("I found my way to user experience through graphic design and slowly over many different roles and experiences.", "我通过平面设计找到了通往用户体验的道路，并在许多不同的角色和经历中慢慢成长。"),
                        ("It took time and commitment to continue to pursue roles within teams that I knew could teach and challenge me.", "这需要时间和投入，继续在那些我知道能教导和挑战我的团队中追求角色。"),
                        ("You can start anywhere as long as you know your end goal and you commit to actively pursue opportunities to learn and grow.", "只要你知道自己的最终目标，并致力于积极追求学习和成长的机会，你可以从任何地方开始。"),
                    ],
                },
                {
                    "id": "cet4-2025-12-itemC2",
                    "name": "Passage Two",
                    "sort_order": 1,
                    "sentences": [
                        ("When planning for this year, our principal asked what needed to change to engage students more in their learning.", "在今年做规划时，我们的校长问需要改变什么才能让学生更多地参与学习。"),
                        ("I responded in a whisper: flexible seating, thinking about our classroom with rows of desks and name plates.", "我低声回答：灵活座位，想着我们那有着一排排课桌和姓名牌的教室。"),
                        ("Flexible seating has been defined as movable furniture to create an engaging learning environment.", "灵活座位被定义为可移动的家具，以创造有吸引力的学习环境。"),
                        ("It is a shift in practice from being teacher focused to student focused learning.", "这是从以教师为中心向以学生为中心学习的实践转变。"),
                        ("For us, flexible seating has meant removing most of the traditional chairs and desks and introducing a variety of seating options.", "对我们来说，灵活座位意味着移除大部分传统桌椅，引入各种座位选择。"),
                        ("Teachers tend to still use the rows format because of either the need to control students or the belief that the teacher is the most important person.", "教师仍然倾向于使用排排坐的形式，要么是因为需要控制学生，要么是认为教师是最重要的人。"),
                        ("Flexible seating enhances student ownership of space and engagement in learning while reducing rates of disengagement.", "灵活座位增强了学生对空间的主人翁感和学习参与度，同时降低了脱离学习的情况。"),
                    ],
                },
                {
                    "id": "cet4-2025-12-itemC3",
                    "name": "Passage Three",
                    "sort_order": 2,
                    "sentences": [
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
        },
    ],
}


# ── 2021年12月 CET-4 真题（第一套）──

NEW_SET_2021 = {
    "id": "cet4-2021-12",
    "name": "2021年12月 CET-4 真题（第一套）",
    "type": "cet4",
    "year": 2021,
    "month": 12,
    "sections": [
        {
            "id": "cet4-2021-12-secA",
            "name": "Section A: News Reports",
            "section_type": "news_report",
            "sort_order": 0,
            "items": [
                {
                    "id": "cet4-2021-12-itemA1",
                    "name": "News Report One",
                    "sort_order": 0,
                    "sentences": [
                        ("Rescue crews in southern Spain have saved dozens of people trapped by severe flooding caused by heavy rain.", "西班牙南部救援人员救出了数十名被暴雨引发的严重洪水围困的民众。"),
                        ("Continuous downpours over two days made local rivers overflow, submerging many residential streets and low-lying houses.", "连续两日的大雨导致当地河水泛滥，淹没多处居民区街道与低洼房屋。"),
                        ("Firefighters used boats to evacuate trapped residents from flooded homes.", "消防员乘坐船只，从被淹住宅中疏散被困居民。"),
                        ("Local government opened several public sports halls as temporary shelters for homeless people.", "当地政府开放多处公共体育馆，作为受灾民众的临时安置点。"),
                        ("Officials warned residents to stay away from river banks as more rainfall is forecast in the coming days.", "有关官员提醒居民远离河岸，未来几日仍有降雨预报。"),
                        ("No deaths have been reported in this flood, though dozens of people suffered minor injuries.", "本次洪水暂无人员遇难报告，但数十人受轻伤。"),
                    ],
                },
                {
                    "id": "cet4-2021-12-itemA2",
                    "name": "News Report Two",
                    "sort_order": 1,
                    "sentences": [
                        ("A newly published report shows that the number of wild bees across Europe has dropped sharply in the past twenty years.", "一份最新发布的报告显示，过去二十年间欧洲野生蜜蜂数量大幅锐减。"),
                        ("Experts point out three major reasons for the decline: widespread use of farm pesticides, loss of wild flower fields due to farmland expansion, and climate change.", "专家指出三大诱因：农田杀虫剂的大范围使用、农田扩张造成野生花草用地缩减以及气候变化。"),
                        ("Wild bees play an irreplaceable role in crop pollination, supporting the production of fruits and vegetables.", "野生蜜蜂在农作物授粉环节有着不可替代的作用，保障果蔬作物产出。"),
                        ("Without enough wild bees, local agricultural output will face obvious decline.", "如果野生蜜蜂数量不足，当地农业产量将明显下滑。"),
                        ("Environmental groups are calling on European governments to limit harmful pesticide use and reserve more wild flowering land to protect bee populations.", "环保组织呼吁欧洲各国政府限制有害农药使用，预留更多野生花草用地以保护蜜蜂种群。"),
                    ],
                },
                {
                    "id": "cet4-2021-12-itemA3",
                    "name": "News Report Three",
                    "sort_order": 2,
                    "sentences": [
                        ("London's famous Central Library reopened to the public on Monday after a two-year repair project.", "伦敦知名的中央图书馆在历时两年修缮工程后，于周一重新对外开放。"),
                        ("The old building was built in 1922 and suffered serious roof damage after heavy storms three years ago.", "这座老建筑始建于1922年，三年前受强暴风雨侵袭，屋顶损毁严重。"),
                        ("Repair workers replaced broken roof materials and fixed old indoor facilities while keeping the library's original classic architectural style.", "修缮工人更换破损屋顶建材、修整老旧室内设施，同时完整保留图书馆原有的经典建筑风格。"),
                        ("The library adds a new children's reading zone and digital resource room during the renovation.", "改造期间图书馆新增儿童阅览区与数字资源室。"),
                        ("Library managers say daily opening hours will be extended by two hours, and all books and digital resources are free for local citizens to borrow and use.", "图书馆负责人表示，每日开放时长延长两小时，所有纸质藏书与数字资源对本地市民免费借阅使用。"),
                    ],
                },
            ],
        },
        {
            "id": "cet4-2021-12-secB",
            "name": "Section B: Long Conversations",
            "section_type": "long_conversation",
            "sort_order": 1,
            "items": [
                {
                    "id": "cet4-2021-12-itemB1",
                    "name": "Conversation One",
                    "sort_order": 0,
                    "sentences": [
                        ("Hi, Mark. I heard you are looking for a part-time job these days. Have you found a suitable one?", "嗨，马克，听说你最近在找兼职，找到合适的了吗？"),
                        ("Not yet. I turned down two job offers last week. One is a restaurant waiter, the other works as a supermarket cashier.", "还没有，上周我推掉了两份录用通知，一份是餐厅服务员，另一份是超市收银员。"),
                        ("Why did you refuse them? Both jobs can bring you pocket money.", "为什么拒绝呢？两份工作都能赚取零花钱。"),
                        ("The working time conflicts with my afternoon compulsory courses. I cannot skip classes for part-time work.", "工作时间和我下午的必修课冲突，我不能为了兼职逃课。"),
                        ("That makes sense. What kind of part-time work are you searching for exactly?", "原来是这样。那你想找什么样的兼职？"),
                        ("I hope to find a job related to English writing or tutoring. My major is English, and I want to improve practical skills.", "我希望找英语写作或者家教相关的工作，我的专业是英语，想锻炼实操能力。"),
                        ("I know the university's tutoring center is recruiting student tutors for middle school students now. Working hours are only on weekends.", "我知道学校家教中心正在招募中学生课外辅导老师，只需要周末上班。"),
                        ("That sounds perfect! Where can I submit my application form?", "这太合适了！在哪里递交申请表？"),
                        ("You can fill out forms online on the center's official website before this Friday.", "本周五前在中心官网线上填表即可。"),
                        ("Thanks a lot for the useful information. I will prepare my resume right away.", "非常感谢，我立刻准备简历。"),
                    ],
                },
                {
                    "id": "cet4-2021-12-itemB2",
                    "name": "Conversation Two",
                    "sort_order": 1,
                    "sentences": [
                        ("Hello, Susan. Do you have plans for the coming holiday break?", "你好苏珊，马上假期了，你有出行计划吗？"),
                        ("I plan to go to a coastal city with my parents for a five-day trip.", "我打算和父母去一座海滨城市玩五天。"),
                        ("That sounds wonderful. Which coastal city will you visit?", "很不错，准备去哪个海滨城市？"),
                        ("Qingdao. We have booked a seaside hotel close to the beach.", "青岛，我们已经预订了临近沙滩的海景酒店。"),
                        ("I've been there before. Local seafood and coastal scenery are really amazing. By the way, have you booked train tickets?", "我之前去过那里，当地海鲜和海滨风光特别棒。对了，火车票订好了吗？"),
                        ("Not yet, the holiday ticket reservation is extremely tight these days. I plan to buy high-speed rail tickets tomorrow morning.", "还没有，假期车票一票难求，我打算明天早上抢高铁票。"),
                        ("You'd better finish booking as soon as possible. Many tickets get sold out quickly during vacation.", "尽量尽早订票，节假日车票很快售罄。"),
                        ("Right, I will set an early alarm tomorrow. What about your holiday arrangement?", "没错，我明天定闹钟早起抢票。那你假期怎么安排？"),
                        ("I will stay on campus and finish my graduation paper. The submission deadline is early next month.", "留校写毕业论文，下月初就要提交定稿。"),
                        ("All the best with your paper writing! I will bring you local seafood snacks after returning.", "祝你写作顺利！我回来给你带当地海鲜特产。"),
                        ("Thank you, have a nice journey.", "谢谢，祝你旅途愉快。"),
                    ],
                },
            ],
        },
        {
            "id": "cet4-2021-12-secC",
            "name": "Section C: Passages",
            "section_type": "passage",
            "sort_order": 2,
            "items": [
                {
                    "id": "cet4-2021-12-itemC1",
                    "name": "Passage One",
                    "sort_order": 0,
                    "sentences": [
                        ("Many parents choose to send their children to different hobby training classes on weekends, including painting, dancing, musical instrument and sports courses.", "很多家长选择在周末送孩子参加各类兴趣培训班，包含绘画、舞蹈、乐器以及体育运动课程。"),
                        ("Some parents believe these courses can help children develop all-round abilities and cultivate extra interests.", "部分家长认为兴趣课能够帮助孩子全面发展、培养特长。"),
                        ("However, more and more educational experts hold different opinions.", "但越来越多的教育专家持不同看法。"),
                        ("They point out too many after-school training courses take up children's rest and outdoor activity time.", "他们指出过量课外培训挤占孩子休息与户外活动时间。"),
                        ("Kids are overburdened with heavy study tasks and easily feel tired and anxious.", "繁重课业压力让孩子身心疲惫、产生焦虑情绪。"),
                        ("Experts suggest parents respect children's personal willingness.", "专家建议家长尊重孩子自身意愿。"),
                        ("If a kid shows no interest in certain hobbies, forcing training will get opposite results.", "如果孩子对某项特长毫无兴趣，强迫培训只会适得其反。"),
                        ("It's better to leave enough spare time for children to play outdoors and develop interests naturally.", "应当留出充足空余时间，让孩子户外玩耍、顺其自然培养爱好。"),
                    ],
                },
                {
                    "id": "cet4-2021-12-itemC2",
                    "name": "Passage Two",
                    "sort_order": 1,
                    "sentences": [
                        ("Walking is one of the easiest and most affordable daily sports for ordinary people.", "步行是普通人门槛最低、成本最小的日常运动。"),
                        ("Unlike swimming or ball games, walking requires no special sports equipment and extra venue fees.", "不同于游泳或球类运动，步行不需要专业器材，也不用支付场地费用。"),
                        ("People can walk on neighborhood paths, city parks or sidewalks whenever they have free time.", "人们有空时可以在小区步道、城市公园或者人行道散步。"),
                        ("Medical research proves that regular daily walking effectively improves blood circulation, strengthens heart function and helps control body weight.", "医学研究证实，每日规律步行能够促进血液循环、增强心肺功能、控制体重。"),
                        ("Besides, taking a slow walk after meals helps digest food and releases daily work pressure.", "除此之外，饭后慢走有助消化，舒缓日常工作压力。"),
                        ("Doctors recommend people to keep 30-minute walking exercise every day, and maintain a relaxed pace instead of walking too fast.", "医生建议每日坚持30分钟步行，保持舒缓步伐，不必快步疾走。"),
                    ],
                },
                {
                    "id": "cet4-2021-12-itemC3",
                    "name": "Passage Three",
                    "sort_order": 2,
                    "sentences": [
                        ("Online shopping has greatly changed people's daily consumption habits over the past decade.", "过去十年，网购极大改变了大众消费习惯。"),
                        ("Consumers can search for products, compare prices and finish payment at home without visiting physical stores.", "消费者足不出户就能选购商品、比价付款，不用前往实体门店。"),
                        ("Online shops cut down costs such as store rent and shop assistants' salary, so most online goods have lower prices than offline counterparts.", "网店省去门店租金、店员薪酬等开支，多数商品售价低于实体店。"),
                        ("However, online shopping also has obvious drawbacks.", "但网购短板同样突出。"),
                        ("Customers cannot touch or try on goods before purchase, leading to frequent return problems caused by size, quality mismatches.", "消费者下单前无法触摸、试用商品，经常因尺码、实物不符产生退货纠纷。"),
                        ("In addition, false advertising and fake products occasionally appear on some small shopping platforms.", "此外，部分小型购物平台不时出现虚假宣传与伪劣产品。"),
                        ("Consumers are advised to choose large official shopping websites and check product comments carefully before placing orders.", "建议消费者优先选择正规大型购物平台，下单前仔细查看用户评价。"),
                    ],
                },
            ],
        },
    ],
}


# ── 2025年12月 CET-4 真题 题目（第一套）──

NEW_SET_QUESTIONS = [
    # ── Section A: News Report One (Q1-Q2) ──
    {"id": "cet4-2025-12-q1", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA1", "question_number": 1, "question_text": "Where was the black cat found?", "question_text_zh": "这只黑猫是在哪里被发现的？", "option_a": "Under a car engine cover.", "option_b": "In a school classroom.", "option_c": "Inside a delivery truck.", "option_d": "Beside a roadside garden.", "correct_answer": "A", "sort_order": 0},
    {"id": "cet4-2025-12-q2", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA1", "question_number": 2, "question_text": "What do we learn about the cat at the end of the news report?", "question_text_zh": "在这篇新闻报道的结尾，我们了解到了关于这只猫的哪些情况？", "option_a": "It was badly injured in the trip.", "option_b": "It was taken in by the car owner.", "option_c": "It was returned to its owner finally.", "option_d": "It was sent to an animal hospital.", "correct_answer": "C", "sort_order": 1},
    # ── Section A: News Report Two (Q3-Q4) ──
    {"id": "cet4-2025-12-q3", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA2", "question_number": 3, "question_text": "What will Fayetteville witness in less than a month?", "question_text_zh": "在不到一个月的时间里，费耶特维尔将见证什么？", "option_a": "A national sports meeting.", "option_b": "The return of Special Olympics Spring Games.", "option_c": "A volunteer recruitment campaign.", "option_d": "An athletes training program.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2025-12-q4", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA2", "question_number": 4, "question_text": "What did Benjamin Kowalzik say is rewarding to see?", "question_text_zh": "Benjamin Kowalzik说什么是有成就感的？", "option_a": "Athletes winning big prizes easily.", "option_b": "Children having fun in the activity tent.", "option_c": "More people signing up to be volunteers.", "option_d": "Disabled athletes achieving success in games.", "correct_answer": "D", "sort_order": 1},
    # ── Section A: News Report Three (Q5-Q7) ──
    {"id": "cet4-2025-12-q5", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA3", "question_number": 5, "question_text": "What has the German supermarket been ordered to do?", "question_text_zh": "这家德国超市被勒令做什么？", "option_a": "Destroy all its chocolate rabbit products.", "option_b": "Stop selling all kinds of chocolate goods.", "option_c": "Pay huge fines to the Swiss manufacturer.", "option_d": "Change the color of product wrappers.", "correct_answer": "A", "sort_order": 0},
    {"id": "cet4-2025-12-q6", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA3", "question_number": 6, "question_text": "What did Switzerland's highest court suggest about the chocolate in question?", "question_text_zh": "瑞士最高法院对涉案巧克力提出了什么建议？", "option_a": "Sell them at a lower price quickly.", "option_b": "Donate them to local poor families.", "option_c": "Melt them to make other chocolate food.", "option_d": "Repackage them with new decorations.", "correct_answer": "C", "sort_order": 1},
    {"id": "cet4-2025-12-q7", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secA", "item_id": "cet4-2025-12-itemA3", "question_number": 7, "question_text": "Why did Switzerland's highest court overturn the commercial court's ruling?", "question_text_zh": "瑞士最高法院为什么推翻了商事法院的裁决？", "option_a": "The German products sold much better.", "option_b": "The two products are easy to be confused.", "option_c": "The Swiss side failed to provide enough evidence.", "option_d": "The commercial court was bribed unfairly.", "correct_answer": "B", "sort_order": 2},
    # ── Section B: Conversation One (Q8-Q11) ──
    {"id": "cet4-2025-12-q8", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB1", "question_number": 8, "question_text": "What does the man request the woman to do?", "question_text_zh": "男士请求女士做什么？", "option_a": "Prepare some fresh vegetables.", "option_b": "Learn to make a simple salad.", "option_c": "Pick up his sister's boyfriend.", "option_d": "Pass him a recipe book.", "correct_answer": "D", "sort_order": 0},
    {"id": "cet4-2025-12-q9", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB1", "question_number": 9, "question_text": "What does the woman say about eating vegetables only?", "question_text_zh": "女士对只吃蔬菜有什么看法？", "option_a": "It is not a well-balanced diet.", "option_b": "It is good for people's health.", "option_c": "It is popular among young people.", "option_d": "It needs plenty of cooking skills.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2025-12-q10", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB1", "question_number": 10, "question_text": "Why does the boyfriend of the man's sister choose to be a vegetarian?", "question_text_zh": "男士姐姐的男朋友为什么选择做素食主义者？", "option_a": "He wants to keep slim and fit.", "option_b": "His religious belief requires it.", "option_c": "He is an advocate of animal protection.", "option_d": "He suffers from certain diseases.", "correct_answer": "C", "sort_order": 2},
    {"id": "cet4-2025-12-q11", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB1", "question_number": 11, "question_text": "On what point does the man agree with the woman at the end of the conversation?", "question_text_zh": "对话结尾男士在哪一点上同意女士？", "option_a": "Zoos should be cancelled completely.", "option_b": "It is hard for them to stick to vegetarian diet.", "option_c": "Animals in zoos live in great pain.", "option_d": "Hot dogs are unhealthy fast food.", "correct_answer": "B", "sort_order": 3},
    # ── Section B: Conversation Two (Q12-Q15) ──
    {"id": "cet4-2025-12-q12", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB2", "question_number": 12, "question_text": "What part of the TV program does the man say was interesting?", "question_text_zh": "男士说电视节目的哪一部分有趣？", "option_a": "Ways to choose comfortable flights.", "option_b": "Advice on choosing travel destinations.", "option_c": "Knowledge about air safety rules.", "option_d": "Tips on getting over jet lag.", "correct_answer": "D", "sort_order": 0},
    {"id": "cet4-2025-12-q13", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB2", "question_number": 13, "question_text": "What does the man say he will do next time he flies a long distance?", "question_text_zh": "男士说他下次长途飞行会怎么做？", "option_a": "Follow the expert's advice on long flights.", "option_b": "Have enough meals during the flight.", "option_c": "Take a good sleep on the plane in advance.", "option_d": "Read related articles before travelling.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2025-12-q14", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB2", "question_number": 14, "question_text": "Why does the woman think she is lucky?", "question_text_zh": "女士为什么认为自己是幸运的？", "option_a": "She seldom takes long-distance flights.", "option_b": "She has learned ways to beat jet lag.", "option_c": "She can still adapt to different time zones easily.", "option_d": "She never feels tired after long journeys.", "correct_answer": "C", "sort_order": 2},
    {"id": "cet4-2025-12-q15", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secB", "item_id": "cet4-2025-12-itemB2", "question_number": 15, "question_text": "Why does the woman think the problem of being afraid to fly deserves attention?", "question_text_zh": "女士为什么认为害怕飞行的问题值得关注？", "option_a": "It has caused many traffic accidents.", "option_b": "A large number of people have this problem.", "option_c": "It will affect people's mental health seriously.", "option_d": "Few people know how to solve this problem.", "correct_answer": "B", "sort_order": 3},
    # ── Section C: Passage One (Q16-Q18) ──
    {"id": "cet4-2025-12-q16", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC1", "question_number": 16, "question_text": "What does the speaker think is the best way to get started in user experience design?", "question_text_zh": "演讲者认为入门用户体验设计的最佳方式是什么？", "option_a": "Master various professional textbooks.", "option_b": "Take part in different training courses.", "option_c": "Learn design skills from famous designers.", "option_d": "Accumulate practical working experience.", "correct_answer": "D", "sort_order": 0},
    {"id": "cet4-2025-12-q17", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC1", "question_number": 17, "question_text": "What does the speaker say being effective requires?", "question_text_zh": "演讲者说要想有效需要什么？", "option_a": "Strong ability to adapt to changes.", "option_b": "Rich knowledge of fine arts.", "option_c": "Good communication skills with clients.", "option_d": "Mastery of all kinds of design software.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2025-12-q18", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC1", "question_number": 18, "question_text": "What can people do as long as they know their end goal and strive for it?", "question_text_zh": "只要人们知道最终目标并为之努力，他们可以做什么？", "option_a": "Change career directions timely.", "option_b": "Teach others relevant professional skills.", "option_c": "Seize chances to learn and make progress.", "option_d": "Set up personal design teams early.", "correct_answer": "C", "sort_order": 2},
    # ── Section C: Passage Two (Q19-Q21) ──
    {"id": "cet4-2025-12-q19", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC2", "question_number": 19, "question_text": "Why did the school principal ask what needed to change?", "question_text_zh": "学校校长为什么问需要改变什么？", "option_a": "To reduce students' learning pressure.", "option_b": "To make students more involved in study.", "option_c": "To improve teachers' teaching methods.", "option_d": "To build a more beautiful campus environment.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2025-12-q20", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC2", "question_number": 20, "question_text": "What has flexible seating meant at the speaker's school?", "question_text_zh": "灵活座位在演讲者的学校意味着什么？", "option_a": "Canceling all after-class activities.", "option_b": "Arranging students to sit in fixed seats.", "option_c": "Letting students study outside classrooms.", "option_d": "Replacing traditional desks with various movable seats.", "correct_answer": "D", "sort_order": 1},
    {"id": "cet4-2025-12-q21", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC2", "question_number": 21, "question_text": "What has flexible seating brought about at the speaker's school?", "question_text_zh": "灵活座位在演讲者的学校带来了什么？", "option_a": "It raises students' learning enthusiasm greatly.", "option_b": "It saves a lot of classroom space.", "option_c": "It makes teachers' management easier.", "option_d": "It shortens students' study time.", "correct_answer": "A", "sort_order": 2},
    # ── Section C: Passage Three (Q22-Q25) ──
    {"id": "cet4-2025-12-q22", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC3", "question_number": 22, "question_text": "Why were dozens of British students sent home on Tuesday?", "question_text_zh": "为什么数十名英国学生周二被送回家？", "option_a": "They were late for the first day of school.", "option_b": "They broke the school classroom rules.", "option_c": "Their shoes failed to meet new uniform rules.", "option_d": "They didn't wear complete school uniforms.", "correct_answer": "C", "sort_order": 0},
    {"id": "cet4-2025-12-q23", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC3", "question_number": 23, "question_text": "What can the price of school uniforms Spark among families in financial difficulty?", "question_text_zh": "校服的价格会在经济困难的家庭中引发什么？", "option_a": "It may make children hate going to school.", "option_b": "It may cause worries among those families.", "option_c": "It will change people's consumption habits.", "option_d": "It will lead to the rise of local commodity prices.", "correct_answer": "B", "sort_order": 1},
    {"id": "cet4-2025-12-q24", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC3", "question_number": 24, "question_text": "What did the head teacher think of the school's new uniform rules?", "question_text_zh": "校长对学校的新校服规定有什么看法？", "option_a": "It brings too much trouble to parents.", "option_b": "It is not suitable for poor students.", "option_c": "It needs to be discussed and improved.", "option_d": "It helps improve students' behavior and study.", "correct_answer": "D", "sort_order": 2},
    {"id": "cet4-2025-12-q25", "set_id": "cet4-2025-12", "section_id": "cet4-2025-12-secC", "item_id": "cet4-2025-12-itemC3", "question_number": 25, "question_text": "What did Lucinda May have to do to buy her child the correct pair of shoes?", "question_text_zh": "Lucinda May为了给孩子买一双符合规定的鞋子不得不做了什么？", "option_a": "Borrow money from her own parents.", "option_b": "Complain about the rule to the school.", "option_c": "Buy cheap second-hand shoes for her kid.", "option_d": "Ask the school to reduce uniform costs.", "correct_answer": "A", "sort_order": 3},
]

# ── 2021年12月 CET-4 真题 题目（第一套）──

NEW_SET_2021_QUESTIONS = [
    # ── Section A: News Report One (Q1-Q2) ──
    {"id": "cet4-2021-12-q1", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA1", "question_number": 1, "question_text": "What caused the severe flooding in southern Spain?", "question_text_zh": "是什么导致了西班牙南部的严重洪水？", "option_a": "Sudden ice melting in nearby mountains.", "option_b": "Two days of continuous heavy rainfall.", "option_c": "Man-made damage to river dams.", "option_d": "High tide from nearby ocean.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2021-12-q2", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA1", "question_number": 2, "question_text": "What did local government do for homeless flood victims?", "question_text_zh": "当地政府为无家可归的洪水灾民做了什么？", "option_a": "Provided free medical treatment in hospitals.", "option_b": "Arranged temporary accommodation in sports halls.", "option_c": "Sent food and clothes door to door.", "option_d": "Moved all residents to higher ground permanently.", "correct_answer": "B", "sort_order": 1},
    # ── Section A: News Report Two (Q3-Q4) ──
    {"id": "cet4-2021-12-q3", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA2", "question_number": 3, "question_text": "What is the main problem mentioned in the news report?", "question_text_zh": "新闻报道中提到的主要问题是什么？", "option_a": "Europe's fruit production keeps falling yearly.", "option_b": "Wild bee numbers in Europe have decreased greatly.", "option_c": "Pesticide pollution damages European farmland.", "option_d": "Many wild flowers disappear across European countries.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2021-12-q4", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA2", "question_number": 4, "question_text": "What do environmental organizations urge governments to do?", "question_text_zh": "环保组织敦促政府做什么？", "option_a": "Develop new pollution-free pesticides.", "option_b": "Build special breeding bases for wild bees.", "option_c": "Restrict harmful pesticides and protect flower fields.", "option_d": "Change traditional crop planting patterns.", "correct_answer": "C", "sort_order": 1},
    # ── Section A: News Report Three (Q5-Q7) ──
    {"id": "cet4-2021-12-q5", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA3", "question_number": 5, "question_text": "Why was London Central Library closed for two years?", "question_text_zh": "伦敦中央图书馆为什么关闭了两年？", "option_a": "It was undergoing large-scale renovation work.", "option_b": "It lacked funds to maintain daily operation.", "option_c": "Its surrounding roads were under construction.", "option_d": "It needed to sort out massive old books.", "correct_answer": "A", "sort_order": 0},
    {"id": "cet4-2021-12-q6", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA3", "question_number": 6, "question_text": "When was the Central Library originally constructed?", "question_text_zh": "中央图书馆最初建于何时？", "option_a": "In 1922.", "option_b": "Three years ago.", "option_c": "Twenty years ago.", "option_d": "Two years ago.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2021-12-q7", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secA", "item_id": "cet4-2021-12-itemA3", "question_number": 7, "question_text": "What new service does the library provide after reopening?", "question_text_zh": "图书馆重新开放后提供了什么新服务？", "option_a": "Free professional training courses.", "option_b": "New children's area and digital resource room.", "option_c": "Free shuttle buses for distant readers.", "option_d": "Outdoor book markets every weekend.", "correct_answer": "B", "sort_order": 2},
    # ── Section B: Conversation One (Q8-Q11) ──
    {"id": "cet4-2021-12-q8", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB1", "question_number": 8, "question_text": "What has Mark done with two part-time job offers?", "question_text_zh": "Mark对两份兼职录用通知做了什么？", "option_a": "He accepted both of them immediately.", "option_b": "He refused these two job opportunities.", "option_c": "He postponed his final decision temporarily.", "option_d": "He recommended them to his classmates.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2021-12-q9", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB1", "question_number": 9, "question_text": "What is the main reason for Mark's refusal?", "question_text_zh": "Mark拒绝的主要原因是什么？", "option_a": "The salary is far below his expectation.", "option_b": "Working time clashes with his classes.", "option_c": "Working environment is too noisy.", "option_d": "The job content is too difficult for him.", "correct_answer": "B", "sort_order": 1},
    {"id": "cet4-2021-12-q10", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB1", "question_number": 10, "question_text": "What kind of part-time job does Mark prefer?", "question_text_zh": "Mark更喜欢哪种兼职工作？", "option_a": "Jobs related to English tutoring or writing.", "option_b": "Weekend jobs in campus cafeteria.", "option_c": "Offline sales work in downtown stores.", "option_d": "Part-time jobs for newspaper delivery.", "correct_answer": "A", "sort_order": 2},
    {"id": "cet4-2021-12-q11", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB1", "question_number": 11, "question_text": "Where should Mark hand in his application?", "question_text_zh": "Mark应该在哪里递交申请？", "option_a": "Submit paper forms at the tutoring center office.", "option_b": "Send application via the official website online.", "option_c": "Email his resume to the woman's mailbox.", "option_d": "Hand in documents to his major teacher.", "correct_answer": "B", "sort_order": 3},
    # ── Section B: Conversation Two (Q12-Q15) ──
    {"id": "cet4-2021-12-q12", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB2", "question_number": 12, "question_text": "What is Susan's holiday plan?", "question_text_zh": "Susan的假期计划是什么？", "option_a": "Travel to Qingdao with her parents.", "option_b": "Finish her school paper at home.", "option_c": "Visit her relatives in coastal towns.", "option_d": "Take part in a seaside volunteer activity.", "correct_answer": "A", "sort_order": 0},
    {"id": "cet4-2021-12-q13", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB2", "question_number": 13, "question_text": "What trouble does Susan meet about the trip?", "question_text_zh": "Susan的旅行遇到了什么麻烦？", "option_a": "She cannot find suitable accommodation.", "option_b": "It's hard to buy holiday train tickets.", "option_c": "Her parents change travel destination suddenly.", "option_d": "The local weather is not suitable for travelling.", "correct_answer": "B", "sort_order": 1},
    {"id": "cet4-2021-12-q14", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB2", "question_number": 14, "question_text": "What will the man do during the holiday?", "question_text_zh": "男士假期会做什么？", "option_a": "Have a self-driving trip to the seaside.", "option_b": "Take a part-time job near the campus.", "option_c": "Stay at school to complete graduation paper.", "option_d": "Attend a short-term professional training.", "correct_answer": "C", "sort_order": 2},
    {"id": "cet4-2021-12-q15", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secB", "item_id": "cet4-2021-12-itemB2", "question_number": 15, "question_text": "What will Susan bring back for the man after travel?", "question_text_zh": "Susan旅行后会给男士带回什么？", "option_a": "Handmade local crafts.", "option_b": "Delicious seafood snacks.", "option_c": "A set of local scenic postcards.", "option_d": "Special local fruit products.", "correct_answer": "B", "sort_order": 3},
    # ── Section C: Passage One (Q16-Q18) ──
    {"id": "cet4-2021-12-q16", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC1", "question_number": 16, "question_text": "What's the common practice among many parents on weekends?", "question_text_zh": "许多家长在周末的常见做法是什么？", "option_a": "Accompany kids to take various hobby training lessons.", "option_b": "Organize family outdoor sports regularly.", "option_c": "Buy many storybooks for children's reading.", "option_d": "Invite private teachers for home tutoring.", "correct_answer": "A", "sort_order": 0},
    {"id": "cet4-2021-12-q17", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC1", "question_number": 17, "question_text": "What negative effect do too many training classes bring to kids?", "question_text_zh": "过多的培训班给孩子带来什么负面影响？", "option_a": "They lose enthusiasm for formal school courses.", "option_b": "They suffer tiredness and mental anxiety.", "option_c": "They refuse all kinds of outdoor activities.", "option_d": "They have conflicts with their parents frequently.", "correct_answer": "B", "sort_order": 1},
    {"id": "cet4-2021-12-q18", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC1", "question_number": 18, "question_text": "What is experts' suggestion for parents?", "question_text_zh": "专家对家长的建议是什么？", "option_a": "Sign up fewer high-cost training courses.", "option_b": "Choose courses based on children's own interest.", "option_c": "Compare different training institutions carefully.", "option_d": "Focus only on kids' academic performance.", "correct_answer": "B", "sort_order": 2},
    # ── Section C: Passage Two (Q19-Q21) ──
    {"id": "cet4-2021-12-q19", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC2", "question_number": 19, "question_text": "What's the advantage of walking compared with other sports?", "question_text_zh": "与其他运动相比，步行的优势是什么？", "option_a": "It can burn fat much faster.", "option_b": "It needs no special equipment or venue cost.", "option_c": "It achieves better fitness effects in shorter time.", "option_d": "It is suitable for all people including seriously sick patients.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2021-12-q20", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC2", "question_number": 20, "question_text": "What health benefit can regular walking bring?", "question_text_zh": "规律步行能带来什么健康益处？", "option_a": "Improve heart condition and control weight.", "option_b": "Completely cure chronic stomach diseases.", "option_c": "Help people stay away from all illnesses.", "option_d": "Improve people's sleep environment directly.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2021-12-q21", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC2", "question_number": 21, "question_text": "How long does the doctor advise people to walk each day?", "question_text_zh": "医生建议人们每天步行多长时间？", "option_a": "Half an hour every single day.", "option_b": "One full hour after supper.", "option_c": "Twenty minutes before breakfast.", "option_d": "Forty minutes every other day.", "correct_answer": "A", "sort_order": 2},
    # ── Section C: Passage Three (Q22-Q25) ──
    {"id": "cet4-2021-12-q22", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC3", "question_number": 22, "question_text": "What convenience does online shopping bring to customers?", "question_text_zh": "网购给消费者带来了什么便利？", "option_a": "They can receive goods on the same day of purchase.", "option_b": "They shop at home without going to physical shops.", "option_c": "All online products enjoy free lifetime after-sale service.", "option_d": "Consumers can bargain freely with online shop owners.", "correct_answer": "B", "sort_order": 0},
    {"id": "cet4-2021-12-q23", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC3", "question_number": 23, "question_text": "Why are online products usually cheaper?", "question_text_zh": "为什么网上的商品通常更便宜？", "option_a": "Online shops save rent and labor costs.", "option_b": "Online merchants purchase goods in huge quantities.", "option_c": "Online platforms offer constant official subsidies.", "option_d": "Online goods have simpler packing standards.", "correct_answer": "A", "sort_order": 1},
    {"id": "cet4-2021-12-q24", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC3", "question_number": 24, "question_text": "What is one main shortcoming of online shopping?", "question_text_zh": "网购的一个主要缺点是什么？", "option_a": "Delivery speed is always uncontrollable.", "option_b": "Customers can't inspect products before buying.", "option_c": "Online payment is not safe enough nowadays.", "option_d": "Return service costs buyers extra money.", "correct_answer": "B", "sort_order": 2},
    {"id": "cet4-2021-12-q25", "set_id": "cet4-2021-12", "section_id": "cet4-2021-12-secC", "item_id": "cet4-2021-12-itemC3", "question_number": 25, "question_text": "What suggestion is given to online shoppers?", "question_text_zh": "给网购者的建议是什么？", "option_a": "Buy discount goods only during big shopping festivals.", "option_b": "Avoid buying cheap products from small platforms.", "option_c": "Pick big formal websites and check user reviews.", "option_d": "Pay after receiving and checking all commodities.", "correct_answer": "C", "sort_order": 3},
]


async def seed_listening_data() -> None:
    db = await get_db()
    try:
        # Seed sets/sections/sentences if empty
        async with db.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM listening_set")
            row = await cur.fetchone()
            if not row or row[0] == 0:
                pass  # fall through to seed
            else:
                row = None  # signal to skip set seeding

        if row is not None:
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
                for item in sec.get("items", []):
                    async with db.cursor() as cur:
                        await cur.execute(
                            "INSERT INTO listening_item(id, set_id, section_id, name, sort_order) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                            (item["id"], ns["id"], sec["id"], item["name"], item["sort_order"]),
                        )
                        for i, (en, zh) in enumerate(item["sentences"]):
                            await cur.execute(
                                "INSERT INTO listening_sentence(id, set_id, section_id, item_id, en, zh, sort_order) VALUES(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE en=VALUES(en), zh=VALUES(zh)",
                                (f"{item['id']}-s{i+1}", ns["id"], sec["id"], item["id"], en, zh, i),
                            )

            await db.commit()

        # Always seed 2021-12 set (safe: ON DUPLICATE KEY UPDATE)
        ns21 = NEW_SET_2021
        async with db.cursor() as cur:
            await cur.execute(
                "INSERT INTO listening_set(id, name, type, year, month, set_order) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                (ns21["id"], ns21["name"], ns21["type"], ns21["year"], ns21["month"], 0),
            )
        for sec in ns21["sections"]:
            async with db.cursor() as cur:
                await cur.execute(
                    "INSERT INTO listening_section(id, set_id, name, section_type, sort_order) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                    (sec["id"], ns21["id"], sec["name"], sec["section_type"], sec["sort_order"]),
                )
            for item in sec.get("items", []):
                async with db.cursor() as cur:
                    await cur.execute(
                        "INSERT INTO listening_item(id, set_id, section_id, name, sort_order) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                        (item["id"], ns21["id"], sec["id"], item["name"], item["sort_order"]),
                    )
                    for i, (en, zh) in enumerate(item["sentences"]):
                        await cur.execute(
                            "INSERT INTO listening_sentence(id, set_id, section_id, item_id, en, zh, sort_order) VALUES(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE en=VALUES(en), zh=VALUES(zh)",
                            (f"{item['id']}-s{i+1}", ns21["id"], sec["id"], item["id"], en, zh, i),
                        )
        await db.commit()

        # Seed questions (always check — handles upgrade from old schema)
        async with db.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM listening_question")
            q_row = await cur.fetchone()
            if not q_row or q_row[0] == 0:
                for qs in (NEW_SET_QUESTIONS, NEW_SET_2021_QUESTIONS):
                    for q in qs:
                        await cur.execute(
                            "INSERT INTO listening_question(id, set_id, section_id, item_id, question_number, question_text, question_text_zh, option_a, option_b, option_c, option_d, correct_answer, sort_order) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE question_text=VALUES(question_text), question_text_zh=VALUES(question_text_zh), correct_answer=VALUES(correct_answer)",
                            (q["id"], q["set_id"], q["section_id"], q.get("item_id"), q["question_number"], q["question_text"], q.get("question_text_zh", ""), q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"], q["sort_order"]),
                        )
                await db.commit()
            else:
                # Always update options for existing questions (handles data upgrades)
                for qs in (NEW_SET_QUESTIONS, NEW_SET_2021_QUESTIONS):
                    for q in qs:
                        await cur.execute(
                            "INSERT INTO listening_question(id, set_id, section_id, item_id, question_number, question_text, question_text_zh, option_a, option_b, option_c, option_d, correct_answer, sort_order) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE question_text=VALUES(question_text), question_text_zh=VALUES(question_text_zh), option_a=VALUES(option_a), option_b=VALUES(option_b), option_c=VALUES(option_c), option_d=VALUES(option_d), correct_answer=VALUES(correct_answer)",
                            (q["id"], q["set_id"], q["section_id"], q.get("item_id"), q["question_number"], q["question_text"], q.get("question_text_zh", ""), q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"], q["sort_order"]),
                        )
                await db.commit()
    finally:
        await release_db(db)
