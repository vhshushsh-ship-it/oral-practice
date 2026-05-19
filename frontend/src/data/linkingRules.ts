import type { LinkingRule } from '../types';

export const linkingRules: LinkingRule[] = [
  {
    id: 'consonant-vowel',
    name: '辅元连读',
    nameEn: 'Consonant-Vowel Linking',
    description: '当一个单词以辅音结尾，下一个单词以元音开头时，辅音与元音连起来读，听起来像一个词。这是英语中最常见的连读现象。',
    examples: [
      { original: 'Pick it up.', linked: 'Pi-ki-tup', translation: '把它捡起来。' },
      { original: 'Not at all.', linked: 'No-ta-tall', translation: '一点也不。' },
      { original: 'I like it a lot.', linked: 'I li-ki-ta lot', translation: '我非常喜欢。' },
    ],
  },
  {
    id: 'vowel-vowel',
    name: '元元连读',
    nameEn: 'Vowel-Vowel Linking (Glide Insertion)',
    description: '当一个单词以元音结尾，下一个单词以元音开头时，中间会自然滑入一个 /j/（类似"耶"）或 /w/（类似"乌"）的过渡音，使两个元音平滑连接。',
    examples: [
      { original: 'See it.', linked: 'See(y)it', translation: '看见它。' },
      { original: 'Go out.', linked: 'Go(w)out', translation: '出去。' },
      { original: 'Do it again.', linked: 'Do(w)it again', translation: '再做一次。' },
    ],
  },
  {
    id: 'elision',
    name: '失爆连读',
    nameEn: 'Elision (Unreleased Stops)',
    description: '当爆破音（/p/ /b/ /t/ /d/ /k/ /g/）后面紧跟另一个辅音时，前面的爆破音只做口型不送气，几乎听不到。这是地道美式口音的关键特征。',
    examples: [
      { original: 'Good morning.', linked: 'Goo(d) morning', translation: '早上好。' },
      { original: 'Stop talking.', linked: 'Sto(p) talking', translation: '别说话。' },
      { original: 'I can\'t go.', linked: 'I can\'(t) go', translation: '我不能去。' },
    ],
  },
  {
    id: 'assimilation',
    name: '同化连读',
    nameEn: 'Assimilation',
    description: '一个音受相邻音的影响而变成与其相近的音。最常见的是 /n/ 在 /b/ /p/ /m/ 前变成 /m/，以及 /t/ /d/ 在 /k/ /g/ 前变成 /k/ /g/。',
    examples: [
      { original: 'Ten bikes.', linked: 'Tem bikes', translation: '十辆自行车。' },
      { original: 'Good boy.', linked: 'Goob boy', translation: '好孩子。' },
      { original: 'That cat.', linked: 'Thak cat', translation: '那只猫。' },
    ],
  },
  {
    id: 'flapping',
    name: '弹舌音',
    nameEn: 'Flapping / Tapping',
    description: '在美式英语中，当 /t/ 或 /d/ 位于两个元音之间（且后一个音节非重读）时，舌尖快速弹一下上齿龈，发出类似 /d/ 的轻快音 [ɾ]。如 water 听起来像 "wadder"。',
    examples: [
      { original: 'Water.', linked: 'Wa[ɾ]er', translation: '水。' },
      { original: 'Better.', linked: 'Be[ɾ]er', translation: '更好的。' },
      { original: 'Get it done.', linked: 'Ge[ɾ] i[ɾ] done', translation: '把它做完。' },
    ],
  },
  {
    id: 'linking-r',
    name: 'R 连读',
    nameEn: 'Linking R / Intrusive R',
    description: '在英式/澳式英语中，当一个单词以元音结尾、下一个以元音开头时，中间会插入一个 /r/ 音来连接。美式英语中也有类似现象，如 "idea of" 读作 "idea(r) of"。',
    examples: [
      { original: 'Law and order.', linked: 'Law(r) and order', translation: '法律与秩序。' },
      { original: 'The idea of it.', linked: 'The idea(r) of it', translation: '关于它的想法。' },
      { original: 'China and Japan.', linked: 'China(r) and Japan', translation: '中国和日本。' },
    ],
  },
  {
    id: 'h-dropping',
    name: 'H 省略',
    nameEn: 'H-Dropping',
    description: '在快速口语中，非重读的功能词（如 him, her, his, have, has）开头的 /h/ 经常被省略，前一个词的辅音直接与后面的元音连读。',
    examples: [
      { original: 'Tell him.', linked: 'Tell \'im', translation: '告诉他。' },
      { original: 'I like her.', linked: 'I like \'er', translation: '我喜欢她。' },
      { original: 'Should have gone.', linked: 'Should \'ave gone', translation: '本该去的。' },
    ],
  },
  {
    id: 'contractions',
    name: '口语缩读',
    nameEn: 'Informal Contractions',
    description: '日常口语中高频词组会缩合成一个词，如 going to → gonna。这些缩读不是"错误"，而是母语者自然流畅表达的方式。',
    examples: [
      { original: 'I\'m going to go.', linked: 'I\'m gonna go', translation: '我准备走了。' },
      { original: 'Do you want to try?', linked: 'Do you wanna try?', translation: '你想试试吗？' },
      { original: 'I\'ve got to leave.', linked: 'I\'ve gotta leave', translation: '我得走了。' },
    ],
  },
];
