import { useState, useCallback, useRef } from 'react';
import type { DialogueScene } from '../types';

// 从原 app.js 提取的场景对话数据
const defaultDialogues: DialogueScene[] = [
  {
    id: 'restaurant',
    name: '🍽️ 餐厅点餐用餐',
    turns: [
      { speaker: 'Waiter', en: 'Welcome! How many people are dining today?', zh: '欢迎光临！请问几位用餐？' },
      { speaker: 'You', en: "Table for two, please. We'd prefer a quiet corner.", zh: '两位，麻烦安排一个安静的角落。' },
      { speaker: 'Waiter', en: 'Of course. Right this way. Here are your menus.', zh: '没问题，这边请。这是菜单。' },
      { speaker: 'You', en: 'Thank you. What do you recommend today?', zh: '谢谢。今天有什么推荐的菜吗？' },
      { speaker: 'Waiter', en: 'Our grilled salmon with lemon butter sauce is excellent. The roasted chicken with rosemary is also very popular.', zh: '我们的柠檬黄油烤三文鱼非常棒。迷迭香烤鸡也很受欢迎。' },
      { speaker: 'You', en: "I'll have the grilled salmon, please. And a side salad.", zh: '我要烤三文鱼，再加一份沙拉。' },
      { speaker: 'Waiter', en: 'Great choice. Would you like anything to drink?', zh: '选得好。需要喝点什么吗？' },
      { speaker: 'You', en: 'A glass of white wine, please.', zh: '请来一杯白葡萄酒。' },
      { speaker: 'Waiter', en: "I'll put your order in right away. It should be ready in about 15 minutes.", zh: '我马上帮您下单，大约15分钟就好。' },
      { speaker: 'You', en: 'Thank you. Could we also have some water?', zh: '谢谢。能给我们来点水吗？' },
    ],
  },
  {
    id: 'interview',
    name: '💼 职场英文面试',
    turns: [
      { speaker: 'Interviewer', en: 'Good morning! Please have a seat. Tell me a little about yourself.', zh: '早上好！请坐。请简单介绍一下你自己。' },
      { speaker: 'You', en: 'Good morning. My name is Li Wei. I graduated from Shanghai University with a degree in Computer Science. I have three years of experience in software development.', zh: '早上好。我叫李伟，毕业于上海大学计算机科学专业，有三年的软件开发经验。' },
      { speaker: 'Interviewer', en: "That's great. Could you tell me about a challenging project you've worked on?", zh: '很好。能跟我说说你做过的一个有挑战性的项目吗？' },
      { speaker: 'You', en: 'Sure. I was part of a team that developed an e-commerce platform. The biggest challenge was optimizing the database queries to handle high traffic.', zh: '当然。我参与了一个电商平台的开发。最大的挑战是优化数据库查询以应对高流量。' },
      { speaker: 'Interviewer', en: 'How did you solve that problem?', zh: '你是怎么解决那个问题的？' },
      { speaker: 'You', en: 'We implemented caching with Redis and rewrote several SQL queries. The page load time improved by 60 percent.', zh: '我们用Redis实现了缓存，并重写了几个SQL查询。页面加载时间提升了60%。' },
    ],
  },
  {
    id: 'hotel',
    name: '🏨 酒店入住办理',
    turns: [
      { speaker: 'Receptionist', en: 'Good evening. Welcome to Grand Hotel. Do you have a reservation?', zh: '晚上好，欢迎来到大酒店。请问有预订吗？' },
      { speaker: 'You', en: 'Yes, I have a reservation under the name Li Wei. I booked a deluxe room for three nights.', zh: '有，我用李伟的名字预订了一间豪华房，住三晚。' },
      { speaker: 'Receptionist', en: "Let me check... Yes, I found your reservation. Could I see your passport, please?", zh: '我查一下……找到了您的预订。请出示一下您的护照。' },
      { speaker: 'You', en: 'Here you go. Is breakfast included?', zh: '给你。房价含早餐吗？' },
      { speaker: 'Receptionist', en: 'Yes, breakfast is served from 7 to 10 a.m. on the second floor. Here is your room key. You are in room 808.', zh: '包含，早餐在二楼，早上7点到10点。这是您的房卡，房间号808。' },
    ],
  },
  {
    id: 'home_life',
    name: '🏠 日常居家交流',
    turns: [
      { speaker: 'Friend', en: "Hey! What's for dinner tonight? I'm getting hungry.", zh: '嘿！今晚吃什么？我有点饿了。' },
      { speaker: 'You', en: "I'm thinking of making some spaghetti with meatballs. Sound good?", zh: '我在想做意大利面配肉丸，怎么样？' },
      { speaker: 'Friend', en: "That sounds amazing! Need any help in the kitchen?", zh: '听起来太棒了！厨房里需要帮忙吗？' },
      { speaker: 'You', en: 'Sure! Could you chop some onions and garlic?', zh: '太好了！你能帮我切点洋葱和大蒜吗？' },
      { speaker: 'Friend', en: 'On it. By the way, did you take out the trash this morning?', zh: '没问题。对了，你今天早上倒垃圾了吗？' },
      { speaker: 'You', en: "Oh, I forgot! I'll do it after dinner. Thanks for reminding me.", zh: '哦，我忘了！晚饭后我去倒。谢谢提醒。' },
    ],
  },
  {
    id: 'directions',
    name: '🗺️ 出行问路乘车',
    turns: [
      { speaker: 'Stranger', en: 'Excuse me, could you help me? I seem to be lost.', zh: '打扰一下，能帮我吗？我好像迷路了。' },
      { speaker: 'You', en: "Of course. Where are you trying to go?", zh: '当然。你要去哪里？' },
      { speaker: 'Stranger', en: "I'm looking for the nearest subway station. Is it within walking distance?", zh: '我在找最近的地铁站。走路能到吗？' },
      { speaker: 'You', en: "Yes, it's about a 10-minute walk. Go straight for two blocks, then turn left at the traffic light. You'll see the station entrance on your right.", zh: '可以的，走路大约十分钟。直走两个街区，然后在红绿灯左转，地铁入口就在右边。' },
    ],
  },
  {
    id: 'shopping',
    name: '🛍️ 商场购物逛街',
    turns: [
      { speaker: 'Salesperson', en: 'Hi there! Looking for something specific today, or just browsing?', zh: '您好！今天想找特定的东西还是随便看看？' },
      { speaker: 'You', en: "I'm looking for a dress for a wedding. Something elegant but not too formal.", zh: '我想找一件参加婚礼穿的裙子，优雅但不要太正式。' },
      { speaker: 'Salesperson', en: 'We have some lovely options in the new collection. What size do you usually wear?', zh: '我们的新款系列有一些不错的选择。您通常穿什么尺码？' },
      { speaker: 'You', en: 'Medium, usually. Can I try this blue one on?', zh: '一般是中号。我能试试这件蓝色的吗？' },
      { speaker: 'Salesperson', en: 'Of course! The fitting rooms are right over there. Let me know if you need a different size.', zh: '当然可以！试衣间就在那边。需要其他尺码随时告诉我。' },
    ],
  },
  {
    id: 'medical',
    name: '🏥 看病就医问诊',
    turns: [
      { speaker: 'Doctor', en: 'Hello. What brings you in today?', zh: '你好。今天哪里不舒服？' },
      { speaker: 'You', en: "I've had a sore throat and a fever for the past two days. I also feel really tired.", zh: '我喉咙痛，发烧两天了，还感觉很累。' },
      { speaker: 'Doctor', en: "Let me take your temperature and check your throat. Say 'ah'.", zh: '我帮你量一下体温，看看喉咙。说"啊"。' },
      { speaker: 'You', en: 'Ah... Is it serious?', zh: '啊……严重吗？' },
      { speaker: 'Doctor', en: "It looks like a throat infection. I'll prescribe some antibiotics. Make sure to drink plenty of water and get some rest.", zh: '看起来是喉咙感染。我给你开点抗生素。记得多喝水，好好休息。' },
    ],
  },
  {
    id: 'campus',
    name: '🎓 校园师生交流',
    turns: [
      { speaker: 'Teacher', en: 'Good morning, class! Today we are going to discuss climate change. Any thoughts on the topic?', zh: '同学们早上好！今天我们讨论气候变化。大家对这个话题有什么想法？' },
      { speaker: 'You', en: 'I think renewable energy is really important. Solar and wind power can help reduce carbon emissions.', zh: '我觉得可再生能源非常重要。太阳能和风能有助于减少碳排放。' },
      { speaker: 'Teacher', en: 'Excellent point. Can you name some countries that are leading in renewable energy?', zh: '很好的观点。你能说出几个在可再生能源方面领先的国家吗？' },
      { speaker: 'You', en: 'Germany and Denmark are doing a lot with wind power. China is also investing heavily in solar energy.', zh: '德国和丹麦在风能方面做了很多。中国也在大力投资太阳能。' },
    ],
  },
  {
    id: 'social',
    name: '🤝 日常社交寒暄',
    turns: [
      { speaker: 'Friend', en: "Hey! Long time no see! How have you been?", zh: '嘿！好久不见！你最近怎么样？' },
      { speaker: 'You', en: "I've been great, thanks! I just got back from a trip to Japan. It was amazing.", zh: '我很好，谢谢！我刚从日本旅游回来，太棒了。' },
      { speaker: 'Friend', en: "That sounds wonderful! What was your favorite part of the trip?", zh: '听起来太棒了！旅行中最喜欢的是什么？' },
      { speaker: 'You', en: 'The food was incredible. I tried so many different dishes. And the temples in Kyoto were breathtaking.', zh: '食物太好吃了，我尝了很多不同的菜。京都的寺庙也美得令人惊叹。' },
    ],
  },
  {
    id: 'phone_chat',
    name: '📱 电话微信沟通',
    turns: [
      { speaker: 'Friend', en: 'Hello? Can you hear me okay?', zh: '喂？能听清楚吗？' },
      { speaker: 'You', en: 'Yes, loud and clear! What are you up to this weekend?', zh: '听得很清楚！你这周末有什么安排？' },
      { speaker: 'Friend', en: "Not much. I was thinking about going to the movies. Want to join?", zh: '没什么特别的。我在想去看电影，一起去吗？' },
      { speaker: 'You', en: "Sure! What movie were you thinking of?", zh: '好啊！你想看哪部电影？' },
      { speaker: 'Friend', en: 'The new action movie just came out. I heard it has great reviews.', zh: '那部新上映的动作片刚出来，听说评价很不错。' },
    ],
  },
  {
    id: 'hobbies',
    name: '🎨 兴趣爱好闲聊',
    turns: [
      { speaker: 'Friend', en: "What do you usually do in your free time? I'm trying to find a new hobby.", zh: '你平时空闲时间都做什么？我想找个新爱好。' },
      { speaker: 'You', en: "I've been into photography lately. There's something special about capturing beautiful moments.", zh: '我最近迷上了摄影。捕捉美好瞬间的感觉很特别。' },
      { speaker: 'Friend', en: "That's cool! What kind of camera do you use?", zh: '真酷！你用什么相机？' },
      { speaker: 'You', en: "Just my phone for now, but I'm saving up for a DSLR. Phone cameras are actually really good these days.", zh: '目前只用手机，但我在存钱买单反。其实现在的手机拍照也相当不错。' },
    ],
  },
  {
    id: 'transport',
    name: '✈️ 机场高铁出行',
    turns: [
      { speaker: 'Staff', en: 'Good morning! May I see your ticket and passport, please?', zh: '早上好！请出示您的机票和护照。' },
      { speaker: 'You', en: 'Here you go. Is the flight on time?', zh: '给你。航班准时吗？' },
      { speaker: 'Staff', en: "Yes, it's on schedule. Your gate is A12, boarding starts at 2:30.", zh: '是的，准点。您的登机口是A12，两点半开始登机。' },
      { speaker: 'You', en: 'Thank you. How many bags can I check in?', zh: '谢谢。我可以托运几件行李？' },
      { speaker: 'Staff', en: 'You can check in two bags. Your carry-on should be under 7 kilograms.', zh: '可以托运两件。随身行李不能超过7公斤。' },
      { speaker: 'You', en: 'Got it. Thanks for your help!', zh: '明白了。谢谢你的帮助！' },
    ],
  },
  {
    id: 'housing',
    name: '🏠 租房看房沟通',
    turns: [
      { speaker: 'Landlord', en: 'Hi! Welcome. Let me show you around the apartment. This is the living room — it gets lots of natural light.', zh: '你好！欢迎，我带你看看公寓。这是客厅，采光非常好。' },
      { speaker: 'You', en: "It looks really nice. How much is the monthly rent?", zh: '看起来真不错。月租是多少？' },
      { speaker: 'Landlord', en: "It's 2500 per month, including water and internet. Electricity is separate.", zh: '每月2500，包含水费和网费，电费另算。' },
      { speaker: 'You', en: "That's within my budget. Is the neighborhood quiet at night?", zh: '在我预算范围内。这附近晚上安静吗？' },
      { speaker: 'Landlord', en: 'Very quiet. The neighbors are mostly families and young professionals. The subway is just a five-minute walk away.', zh: '非常安静。邻居大多是家庭和年轻白领。地铁走路五分钟就到。' },
    ],
  },
];

export function useSceneDialogues() {
  const [dialogues] = useState<DialogueScene[]>(() => {
    try {
      const stored = localStorage.getItem('scene-dialogues');
      return stored ? JSON.parse(stored) : defaultDialogues;
    } catch {
      return defaultDialogues;
    }
  });
  const [selectedScene, setSelectedScene] = useState<DialogueScene | null>(null);
  const scrollPositions = useRef<Record<string, number>>({});

  const selectScene = useCallback(
    (scene: DialogueScene, scrollEl: HTMLElement | null) => {
      if (selectedScene && scrollEl) {
        scrollPositions.current[selectedScene.id] = scrollEl.scrollTop;
      }
      setSelectedScene(scene);
      setTimeout(() => {
        if (scrollEl) {
          scrollEl.scrollTop = scrollPositions.current[scene.id] || 0;
        }
      }, 0);
    },
    [selectedScene],
  );

  return { dialogues, selectedScene, setSelectedScene: selectScene };
}
