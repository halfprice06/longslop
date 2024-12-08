from pydantic import BaseModel

class StyleTransfer(BaseModel):
    name: str
    description: str
    example: str
# Add this constant at the module level
AVAILABLE_STYLES = {

    "hemingway": StyleTransfer(
        name="Hemingway",
        description="""Ernest Hemingway’s writing style is as distinctive as his adventurous life and as impactful as his stories. A Nobel laureate, Hemingway’s approach to prose is often described through his adherence to the “Iceberg Theory,” a technique that demands the writer omit anything superfluous, leaving the deeper meaning of the text to be implicitly understood by the reader. This method results in writing that is lean, direct, and devoid of the ornate flourishes that characterized much of the literature that preceded him.

        Hemingway’s sentences are notoriously short and simple but powerful, with a rhythmic quality that mirrors the action it describes. This simplicity is deceptive; behind the straightforward surface lies a complex understanding of human nature and emotion. Hemingway achieves this depth through his masterful use of dialogue—a tool that lets the characters’ words speak for themselves without overt authorial intrusion. His dialogue often carries the weight of the narrative, pushing the plot forward and deepening character development, all while maintaining a veneer of simplicity.

        The choice of words in Hemingway’s work is meticulously deliberate. He favored concrete nouns and active verbs, eschewing the passive voice and excessive adjectives. This precision not only contributes to the clarity of his prose but also intensifies the scenes he depicts. The sensory details are never lavish but always sufficient to anchor the reader in Hemingway’s vividly real worlds.

        Hemingway’s narrative structure also reflects his distinctive style. He often jumps into scenes without preamble, a technique that places readers immediately into the action and demands their active engagement. The structure of his stories is such that each sentence and scene is essential, with nothing to spare. This economy of language is perhaps Hemingway’s most defining characteristic, influencing countless writers in the generations that followed.

        Through these techniques, Hemingway’s writing remains a paragon of modernist literature, demonstrating that profound complexity can lie beneath deceptively simple surfaces.""",

        example="""That night at the hotel, in our room with the long empty hall outside and our shoes outside the door, a thick carpet on the floor of the room, outside the windows the rain falling and in the room light and pleasant and cheerful, then the light out and it exciting with smooth sheets and the bed comfortable, feeling that we had come home, feeling no longer alone, waking in the night to find the other one there, and not gone away; all other things were unreal. We slept when we were tired and if we woke the other one woke so no one was not alone. Often a man wishes to be alone and a girl wishes to be alone too and if they love each other they are jealous of that in each other, but I can truly say we never felt that. We could feel alone when we were together, alone against the others. It has only happened to me like that once. I have been alone while I Was with many girls and that is the way you can be most lonely. But we were never lonely and never afraid when we were together. I know that the night is not the same as the day: that all things are different, that the things of the night cannot be explained in the day, because they do not then exist, and the night can be a dreadful time for lonely people once their loneliness has started. But with Catherine there was almost no difference in the night except that it was an even better time. If people bring so much courage to this world the world has to kill them to break them, so of course it kills them. The world breaks every one and afterward many are strong at the broken places. But those that will not break it kills. It kills the very good and the very gentle and the very brave impartially. If you are none of these you can be sure it will kill you too but there will be no special hurry. """
    ),

    "mark_twain": StyleTransfer(
        name="Mark Twain",
        
        description="""Mark Twain, the pen name of Samuel Langhorne Clemens, is celebrated not only for his keen wit and deep insight into the human condition, but also for his distinctive writing style, which has captivated readers and influenced writers for over a century. Twain’s style is immediately recognizable for its blend of humor, narrative prowess, and unpretentious language, making his works accessible yet profoundly meaningful.

        Twain’s approach to sentence structure often reflects the rhythms of natural speech, giving his prose a conversational quality that draws readers in. He frequently employs short, punchy sentences that mirror the spoken word, a technique that enhances the immediacy and impact of his narratives. This is interspersed with longer, more complex constructions that add depth and detail, showcasing his skill as a storyteller.

        One of the most distinctive aspects of Twain’s writing is his adept use of dialects and regional vernaculars. This not only adds authenticity to his characters and settings but also enriches the cultural texture of his stories. By capturing the unique voices of various American locales, Twain celebrates the diversity of the nation while also critiquing its social and moral shortcomings.

        Twain’s choice of words often serves a dual purpose: to entertain and to provoke thought. His vocabulary is robust yet straightforward, avoiding unnecessary complexity to ensure clarity and enhance relatability. His adept use of irony and satire is particularly effective, allowing him to address serious social issues with a light touch that can both amuse and enlighten his audience.

        In terms of narrative structure, Twain shows a preference for a loosely connected series of episodes rather than a tightly organized plot. This episodic structure allows him to explore a wide range of scenarios and characters, reflecting the unpredictable twists and turns of real life. The fluidity of his storytelling mirrors the meandering journey of his protagonists, particularly evident in works like “Adventures of Huckleberry Finn.”

        Through these stylistic choices, Twain not only entertains but also challenges his readers to reflect on the moral complexities of society. His writing remains a pivotal element of American literature, demonstrating the power of prose to influence thought and inspire change.""",
        
        example="""Extending the Blessings of Civilization to our Brother who Sits in Darkness has been a good trade and has paid well, on the whole; and there is money in it yet, if carefully worked—but not enough, in my judgment, to make any considerable risk advisable. The People that Sit in Darkness are getting to be too scarce—too scarce and too shy. And such darkness as is now left is really of but an indifferent quality, and not dark enough for the game. The most of those People that Sit in Darkness have been furnished with more light than was good for them or profitable for us. We have been injudicious.

        The Blessings-of-Civilization Trust, wisely and cautiously administered, is a Daisy. There is more money in it, more territory, more sovereignty, and other kinds of emolument, than there is in any other game that is played. But Christendom has been playing it badly of late years, and must certainly suffer" by it, in my opinion. She has been so eager to get every stake that appeared on the green cloth, that the People who Sit in Darkness have noticed it—they have noticed it, and have begun to show alarm. They have become suspicious of the Blessings of Civilization. More—they have begun to examine them. This is not well. The Blessings of Civilization are all right, and a good commercial property; there could not be a better, in a dim light. In the right kind of a light, and at a proper distance, with the goods a little out of focus, they furnish this desirable exhibit to the Gentlemen who Sit in Darkness:"""
    ),

    "jane_austen": StyleTransfer(
        name="Jane Austen",
        
        description="""Jane Austen’s writing style is a beacon of clarity, precision, and social insight, wrapped in a prose that is both engaging and critically sharp. Austen’s novels, written during the late 18th and early 19th centuries, stand out for their wit and their astute commentary on the social fabric of her time. Her approach to narrative, characterized by its indirect free discourse, allows readers a deeper perception of her characters’ inner lives, thoughts, and feelings.

        Austen’s sentence structure often mirrors the complexities of her characters’ social maneuvers. She frequently employs long, elegantly constructed sentences that carefully balance multiple clauses. This reflects not only the formal conventions of her time but also the measured, reflective quality of her protagonists’ internal deliberations. Her use of irony—subtle and yet striking—serves as a critical tool, revealing the contradictions within societal norms and character motivations.

        In her dialogue, Austen shines with a brilliance that captures the rigid, often superficial interaction prescribed by the social etiquette of her day. The dialogue often carries a dual edge—conveying both the superficial social niceties and the deeper, sometimes unspoken tensions between characters. This technique exposes the underlying conflicts and desires that propel the narrative forward, offering a layered understanding of human behavior and social dynamics.

        Austen’s choice of vocabulary is meticulously tailored to fit the context and the character, enhancing authenticity and depth. Her adept use of specific language not only differentiates characters but also subtly critiques the societal roles and expectations imposed upon them. Through her precise word choice and the strategic deployment of irony, Austen crafts narratives that resonate with timeless themes of love, morality, and societal expectation.

        In exploring Austen’s style, one appreciates her unique ability to blend narrative technique with social commentary, all while engaging the reader with stories that resonate across centuries. Her style is not merely a vehicle for storytelling; it is an integral part of the social tapestry she weaves, inviting readers to look beyond the surface into the intricate dynamics of human relationships and societal constraints.""",
        
        example="""It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.

        However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.

        "My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"

        Mr. Bennet replied that he had not.

        "But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."

        Mr. Bennet made no answer.

        "Do not you want to know who has taken it?" cried his wife impatiently.

        "You want to tell me, and I have no objection to hearing it."

        This was invitation enough.

        "Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."

        "What is his name?"

        "Bingley."

        "Is he married or single?"

        "Oh! single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"

        "How so? how can it affect them?"

        "My dear Mr. Bennet," replied his wife, "how can you be so tiresome! You must know that I am thinking of his marrying one of them."

        "Is that his design in settling here?"

        "Design! nonsense, how can you talk so! But it is very likely that he may fall in love with one of them, and therefore you must visit him as soon as he comes."

        "I see no occasion for that. You and the girls may go, or you may send them by themselves, which perhaps will be still better, for as you are as handsome as any of them, Mr. Bingley might like you the best of the party."

        "My dear, you flatter me. I certainly have had my share of beauty, but I do not pretend to be any thing extraordinary now. When a woman has five grown up daughters, she ought to give over thinking of her own beauty."

        "In such cases, a woman has not often much beauty to think of."

        "But, my dear, you must indeed go and see Mr. Bingley when he comes into the neighbourhood."

        "It is more than I engage for, I assure you."

        "But consider your daughters. Only think what an establishment it would be for one of them. Sir William and Lady Lucas are determined to go, merely on that account, for in general you know they visit no new comers. Indeed you must go, for it will be impossible for us to visit him, if you do not."

        "You are over scrupulous surely. I dare say Mr. Bingley will be very glad to see you; and I will send a few lines by you to assure him of my hearty consent to his marrying which ever he chuses of the girls; though I must throw in a good word for my little Lizzy."

        "I desire you will do no such thing. Lizzy is not a bit better than the others; and I am sure she is not half so handsome as Jane, nor half so good humoured as Lydia. But you are always giving her the preference."

        "They have none of them much to recommend them," replied he; "they are all silly and ignorant like other girls; but Lizzy has something more of quickness than her sisters."

        "Mr Bennet, how can you abuse your own children in such a way? You take delight in vexing me. You have no compassion on my poor nerves."

        "You mistake me, my dear. I have a high respect for your nerves. They are my old friends. I have heard you mention them with consideration these twenty years at least."

        "Ah! you do not know what I suffer."

        "But I hope you will get over it, and live to see many young men of four thousand a year come into the neighbourhood."

        "It will be no use to us, if twenty such should come since you will not visit them."

        "Depend upon it, my dear, that when there are twenty, I will visit them all."

        Mr Bennet was so odd a mixture of quick parts, sarcastic humour, reserve, and caprice, that the experience of three and twenty years had been insufficient to make his wife understand his character. Her mind was less difficult to develope. She was a woman of mean understanding, little information and uncertain temper. When she was discontented she fancied herself nervous. The business of her life was to get her daughters married; its solace was visiting and news."""
    ),

    "atwood": StyleTransfer(
        name="Margaret Atwood",
        
        description="""Margaret Atwood’s writing style is a tapestry of precise diction and complex narrative layers that captivate and challenge her readers. Known for her sharp wit and keen observations, Atwood crafts her sentences with a meticulous attention to both rhythm and detail. Her prose often carries a poetic quality, achieved through careful word choice and a mastery of varied sentence structures that keep the reader engaged and reflective.

        Atwood’s approach to narrative structure is equally distinctive. She frequently employs shifting perspectives and non-linear timelines, which allow her to explore the inner lives and historical contexts of her characters more deeply. This technique not only enriches the reader’s understanding but also reflects the fragmented nature of human memory and perception. Atwood’s use of multiple viewpoints often challenges the reader to piece together the story from diverse fragments, much like assembling a jigsaw puzzle without a guiding picture.

        Her themes often explore the intersections of gender, power, and society, and her language reflects this focus. Atwood chooses words that have strong connotations, which imbue her narratives with a sense of urgency and profound insight. Her use of irony and metaphor is particularly effective, offering a critique of societal norms and human behaviors in a manner that is both subtle and impactful.

        Dialogue in Atwood’s works is another element where her skill shines. She captures the voices of her characters with authenticity, using dialogue not only to reveal their personalities but also to advance the plot and deepen thematic explorations. The natural flow of conversation in her books, combined with her sharp, incisive humor, makes the interactions memorable and often laden with deeper meanings.

        In crafting her stories, Atwood does not shy away from experimenting with genre and form. Whether delving into speculative fiction or historical narratives, her style remains consistent in its clarity, complexity, and engagement. This adaptability without loss of voice is a testament to her skill and meticulous craft as a writer, making her works enduringly popular and critically acclaimed.""",
        
        example="""We slept in what had once been the gymnasium. The floor was of varnished wood, with stripes and circles painted on it, for the games that were formerly played there; the hoops for the basketball nets were still in place, though the nets were gone. A balcony ran around the room, for the spectators, and I thought I could smell, faintly like an afterimage, the pungent scent of sweat, shot through with the sweet taint of chewing gum and perfume from the watching girls, felt-skirted as I knew from pictures, later in miniskirts, then pants, then in one earring, spiky green-streaked hair. Dances would have been held there; the music lingered, a palimpsest of unheard sound, style upon style, an undercurrent of drums, a forlorn wail, garlands made of tissue-paper flowers, cardboard devils, a revolving ball of mirrors, powdering the dancers with a snow of light.

        There was old sex in the room and loneliness, and expectation, of something without a shape or name. I remember that yearning, for something that was always about to happen and was never the same as the hands that were on us there and then, in the small of the back, or out back, in the parking lot, or in the television room with the sound turned down and only the pictures flickering over lifting flesh.

        We yearned for the future. How did we learn it, that talent for insatiability? It was in the air; and it was still in the air, an afterthought, as we tried to sleep, in the army cots that had been set up in rows, with spaces between so we could not talk. We had flannelette sheets, like children's, and army-issue blankets, old ones that still said U.S. We folded our clothes neatly and laid them on the stools at the ends of the beds. The lights were turned down but not out. Aunt Sara and Aunt Elizabeth patrolled; they had electric cattle prods slung on thongs from their leather belts.

        No guns though, even they could not be trusted with guns. Guns were for the guards, specially picked from the Angels. The guards weren't allowed inside the building except when called, and we weren't allowed out, except for our walks, twice daily, two by two around the football field, which was enclosed now by a chain-link fence topped with barbed wire. The Angels stood outside it with their backs to us. They were objects of fear to us, but of something else as well. If only they would look. If only we could talk to them. Something could be exchanged, we thought, some deal made, some tradeoff, we still had our bodies. That was our fantasy.

        We learned to whisper almost without sound. In the semidarkness we could stretch out our arms, when the Aunts weren't looking, and touch each other's hands across space. We learned to lip-read, our heads flat on the beds, turned sideways, watching each other's mouths. In this way we exchanged names, from bed to bed:

        Alma. Janine. Dolores. Moira. June."""
    ),

    "edgar_allan_poe": StyleTransfer(
        name="Edgar Allan Poe",
        description="""Edgar Allan Poe, one of the most celebrated writers of the 19th century, is often recognized for his unique and intricate writing style, which has captivated readers and scholars alike. His approach to writing is marked by a meticulous choice of words, an emphasis on atmosphere, and a keen use of rhythm, all of which contribute to the immersive and often haunting quality of his narratives.

        Poe’s sentence structure is notably complex, featuring a liberal use of commas, semicolons, and dashes that help build suspense and emphasize his thematic concerns. This punctuation is not merely decorative; it plays an integral role in shaping the rhythm of his prose, making his narratives feel like a carefully composed score, each element timed to contribute to the overall effect of the story.

        His vocabulary is rich and sometimes archaic, reflecting his background and the era in which he wrote. Poe’s choice of words often serves to elevate the tone of his stories, lending a certain gravitas and formality that is in keeping with the Gothic tradition. This lexical choice enhances the mood and setting, drawing readers deeper into his meticulously crafted worlds.

        Poe also excels in the use of first-person narration, which allows him to explore complex psychological states and unreliable narrators. This technique invites readers into the minds of his protagonists, often blurring the lines between reality and madness. The intimacy of this perspective creates a confessional tone that is both compelling and unsettling, placing the reader in the position of a confidant or voyeur.

        The structure of Poe’s works often reflects his themes of order and chaos, mirroring the internal struggles of his characters. His tales frequently unfold with a precise, almost clinical methodology, then gradually spiral into disorder, reflecting the descent into madness that is a common motif in his writing.

        Edgar Allan Poe’s style is a mix of meticulous craftsmanship and psychological complexity, making his works enduringly fascinating and profoundly unsettling.""",
        
        example="""TRUE!--NERVOUS--very, very dreadfully nervous I had been and am! but why will you say that I am mad? The disease had sharpened my senses--not destroyed--not dulled them. Above all was the sense of hearing acute. I heard all things in the heaven and in the earth. I heard many things in hell. How, then, am I mad? Hearken! and observe how healthily--how calmly I can tell you the whole story.

        It is impossible to say how first the idea entered my brain; but once conceived, it haunted me day and night. Object there was none. Passion there was none. I loved the old man. He had never wronged me. He had never given me insult. For his gold I had no desire. I think it was his eye! yes, it was this! He had the eye of a vulture--a pale blue eye, with a film over it. Whenever it fell upon me, my blood ran cold; and so by degrees--very gradually--I made up my mind to take the life of the old man, and thus rid myself of the eye forever.

        Now this is the point. You fancy me mad. Madmen know nothing. But you should have seen me. You should have seen how wisely I proceeded--with what caution--with what foresight--with what dissimulation I went to work!

        I was never kinder to the old man than during the whole week before I killed him. And every night, about midnight, I turned the latch of his door and opened it--oh, so gently! And then, when I had made an opening sufficient for my head, I put in a dark lantern, all closed, closed, so that no light shone out, and then I thrust in my head. Oh, you would have laughed to see how cunningly I thrust it in! I moved it slowly--very, very slowly, so that I might not disturb the old man's sleep. It took me an hour to place my whole head within the opening so far that I could see him as he lay upon his bed. Ha!--would a madman have been so wise as this? And then, when my head was well in the room, I undid the lantern cautiously--oh, so cautiously--cautiously (for the hinges creaked)--and I undid it just so much that a single thin ray fell upon the vulture eye. And this I did for seven long nights--every night just at midnight--but I found the eye always closed; and so it was impossible to do the work; for it was not the old man who vexed me, but his Evil Eye. And every morning, when the day broke, I went boldly into the chamber, and spoke courageously to him, calling him by name in a hearty tone, and inquiring how he had passed the night. So you see he would have been a very profound old man, indeed, to suspect that every night, just at twelve, I looked in upon him while he slept."""
                    ),

    "isaac_asimov": StyleTransfer(
        name="Isaac Asimov",
        
        description="""Isaac Asimov, a master of science fiction and popular science writing, possessed a distinctive style that was both accessible and engaging. His prose, often characterized by its clarity and straightforwardness, allowed complex ideas to be presented with remarkable simplicity. Asimov favored a direct narrative approach, typically eschewing ornate language or excessive metaphor, which made his vast body of work inviting to a broad audience.

        Asimov’s sentences tended to be concise and functional. He rarely used flowery language or convoluted constructions, preferring instead to communicate ideas and stories in the most straightforward possible manner. This is not to say his writing lacked nuance or depth, but rather that he achieved these qualities through clear, logical progression of thought and a strong command of his subject matter.

        Dialogue in Asimov’s stories often served as a vehicle for exposition and character development. He had a knack for crafting conversations that felt natural yet were imbued with information that moved the plot forward or deepened the reader’s understanding of the science behind the fiction. This technique not only kept his narratives engaging but also educational, a reflection of his own background in academia.

        Structurally, Asimov’s works frequently relied on a logical framework, mirroring his scientific background. Whether in his essays or his fiction, he tended to build his arguments or storylines in a methodical manner, introducing concepts in a sequence that anticipates the reader’s questions and addresses them one by one. This methodical buildup could be seen as a reflection of his scientific training, each piece of information acting like a building block in an experiment or a complex theorem.

        Asimov’s style was a blend of clear exposition, straightforward dialogue, and logical structure, all of which served to make even the most complex ideas or intricate plots accessible and engaging to readers of all levels. His approach has not only helped demystify science but has also left a lasting mark on the genres of science fiction and popular science writing.""",
        
        example=""""Ninety-eight--ninety-nine--one hundred." Gloria withdrew her chubby little forearm from before her eyes and stood for a moment, wrinkling her nose and blinking in the sunlight. Then, trying to watch in all directions at once, she withdrew a few cautious steps from the tree against which she had been leaning.

        She craned her neck to investigate the possibilities of a clump of bushes to the right and then withdrew farther to obtain a better angle for viewing its dark recesses. The quiet was profound except for the incessant buzzing of insects and the occasional chirrup of some hardy bird, braving the midday sun.

        Gloria pouted, "I bet he went inside the house, and I've told him a million times that that's not fair."

        With tiny lips pressed together tightly and a severe frown crinkling her forehead, she moved determinedly toward the two-story building up past the driveway.

        Too late she heard the rustling sound behind her, followed by the distinctive and rhythmic clump-clump of Robbie's metal feet. She whirled about to see her triumphing companion emerge from hiding and make for the home-tree at full speed.

        Gloria shrieked in dismay. "Wait, Robbie! That wasn't fair, Robbie! You promised you wouldn't run until I found you." Her little feet could make no headway at all against Robbie's giant strides. Then, within ten feet of the goal, Robbie's pace slowed suddenly to the merest of crawls, and Gloria, with one final burst of wild speed, dashed pantingly past him to touch the welcome bark of home-tree first.

        Gleefully, she turned on the faithful Robbie, and with the basest of ingratitude, rewarded him for his sacrifice by taunting him cruelly for a lack of running ability.

        "Robbie can't run," she shouted at the top of her eight-year-old voice. "I can beat him any day. I can beat him any day." She chanted the words in a shrill rhythm.

        Robbie didn't answer, of course--not in words. He pantomimed running instead, inching away until Gloria found herself running after him as he dodged her narrowly, forcing her to veer in helpless circles, little arms outstretched and fanning at the air.

        "Robbie," she squealed, "stand still!"--And the laughter was forced out of her in breathless jerks."""
                    ),

    "ray_bradbury": StyleTransfer(
        name="Ray Bradbury",
        
        description="""Ray Bradbury’s writing style is a vibrant tapestry that blends lyrical prose with imaginative narratives, often weaving the fantastic with the ordinary in a way that speaks directly to the reader’s senses. His approach to storytelling is characterized by a poetic rhythm and a rich use of metaphor, which elevate his prose beyond mere communication to an art form that engages the reader on multiple levels.

        Bradbury’s sentences often flow like the verses of a poem, with a musical quality that resonates with readers. He uses repetition effectively, not just for emphasis, but to build a mood or theme throughout his work. This technique, coupled with his choice of evocative words, often transforms his narratives into a sensory experience. Bradbury’s diction is carefully chosen to provoke thought and emotion, reflecting his background in poetry which he credited with teaching him the importance of choosing the right words.

        Dialogue in Bradbury’s works does more than carry the plot forward; it reveals deep insights into his characters’ psyches, often capturing their hopes, fears, and dreams. He had a unique ability to write spoken words that felt authentic and poignant, which helped ground even his most fantastical stories in emotional reality.

        Structurally, Bradbury often embraced a nonlinear approach, especially in his short stories, where he crafted scenes that could stand alone yet contribute to a larger narrative. This method allowed him to explore complex themes from multiple angles, enriching the reader’s understanding and engagement with the material.

        Bradbury’s use of imagery is another hallmark of his style. He had the ability to paint vivid pictures with words, using detailed descriptions that made his fictional worlds feel tangible. This skill not only pulled readers into his stories but also left lasting impressions, making his works unforgettable.

        Ray Bradbury’s writing style is a blend of lyrical expression, thoughtful word choice, and profound thematic exploration, all of which are stitched together with a deep understanding of human emotions and universal truths. His legacy as a writer is not just in the stories he told but in how beautifully he told them.""",
        
        example="""Aimee watched the sky, quietly.

        Tonight was one of those motionless hot summer nights. The concrete pier empty, the strung red, white, yellow bulbs burning like insects in the air above the wooden emptiness. The managers of the various carnival pitches stood, like melting wax dummies, eyes staring blindly, not talking, all down the line.

        Two customers had passed through an hour before. Those two lonely people were now in the roller coaster, screaming murderously as it plummeted down the blazing night, around one emptiness after another.

        Aimee moved slowly across the strand, a few worn wooden hoopla rings sticking to her wet hands. She stopped behind the ticket booth that fronted the MIRROR MAZE. She saw herself grossly misrepresented in three rippled mirrors outside the Maze. A thousand tired replicas of herself dissolved in the corridor beyond, hot images among so much clear coolness.

        She stepped inside the ticket booth and stood looking a long while at Ralph Banghart’s thin neck. He clenched an unlit cigar between his long uneven yellow teeth as he laid out a battered game of solitaire on the ticket shelf.

        When the roller coaster wailed and fell in its terrible avalanche again, she was reminded to speak.

        “What kind of people go up in roller coasters?”

        Ralph Banghart worked his cigar a full thirty seconds. “People wanna die. That rollie coaster’s the handiest thing to dying there is.” He sat listening to the faint sound of rifle shots from the shooting gallery. “This whole damn carny business’s crazy. For instance, that dwarf. You seen him? Every night, pays his dime, runs in the Mirror Maze all the way back through to Screwy Louie’s Room. You should see this little runt head back there. My God!”

        “Oh, yes,” said Aimee, remembering. “I always wonder what it’s like to be a dwarf. I always feel sorry when I see him.”

        “I could play him like an accordion.”

        “Don’t say that!”

        “My Lord.” Ralph patted her thigh with a free hand. “The way you carry on about guys you never even met.” He shook his head and chuckled. “Him and his secret. Only he don’t know I know, see? Boy howdy!"""
    ),

    "shakespeare": StyleTransfer(
        name="William Shakespeare",
        
        description="""William Shakespeare’s writing style is as iconic as the stories he tells. His works, penned in the late 16th and early 17th centuries, continue to captivate audiences with their rich language, complex characters, and intricate plots. A deep dive into his style reveals a masterful command of the English language and a pioneering approach to storytelling.

        Shakespeare’s use of iambic pentameter is perhaps the most distinctive feature of his style. This rhythmic pattern of unstressed and stressed syllables lends a musical quality to his lines, making them memorable and impactful. The constraints of this meter did not limit his creativity; rather, they seemed to fuel it. Shakespeare frequently played with this structure to emphasize certain words or to create a particular emotional effect.

        His vocabulary was extensive, and he had a knack for coining new words and phrases. Many of the terms he introduced have become so ingrained in our language that they remain in common use today. This inventiveness with words allowed him to express complex ideas and emotions more effectively, giving his characters depth and relatability.

        Shakespeare was also a master of metaphor and other figurative language, using them to add layers of meaning to his texts. His metaphors often drew from the natural world, which made his works resonate with universal themes of love, power, betrayal, and mortality. These devices not only beautified his language but also deepened the audience’s engagement with the text by prompting them to think and feel beyond the literal meanings of his words.

        In constructing his plays, Shakespeare often employed a five-act structure, which allowed him to develop his characters and plots with great sophistication. This structure facilitated a buildup of tension and a progression of themes that culminated in dramatic climaxes. His ability to intertwine subplots and main plots with this framework created a rich tapestry of narrative that has been studied and admired for centuries.

        Shakespeare’s writing remains a high watermark for literary achievement. His innovative use of language, his skillful meter, and his profound insight into human nature have left an indelible mark on the world of literature.""",
        
        example="""Enter Barnardo and Francisco, two sentinels Meeting

        BARNARDO Who's there?

        FRANCISCO Nay, answer me: stand and unfold yourself.

        BARNARDO Long live the king!

        FRANCISCO Barnardo?

        BARNARDO He.

        FRANCISCO You come most carefully upon your hour.

        BARNARDO 'Tis now struck twelve: get thee to bed, Francisco.

        FRANCISCO For this relief much thanks: 'tis bitter cold,
        And I am sick at heart.

        BARNARDO Have you had quiet guard?

        FRANCISCO Not a mouse stirring.

        BARNARDO Well, goodnight.
        If you do meet Horatio and Marcellus,
        The rivals of my watch, bid them make haste.

        Enter Horatio and Marcellus

        FRANCISCO I think I hear them.- Stand! Who's there?

        HORATIO Friends to this ground.

        MARCELLUS And liegemen to the Dane.

        FRANCISCO Give you goodnight.

        MARCELLUS O, farewell, honest soldier. Who hath relieved you?

        FRANCISCO Barnardo has my place. Give you goodnight.

        Exit Francisco

        MARCELLUS Holla! Barnardo!

        BARNARDO Say, what, is Horatio there?

        HORATIO A piece of him.

        BARNARDO Welcome, Horatio: welcome, good Marcellus.

        MARCELLUS What, has this thing appeared again tonight?

        BARNARDO I have seen nothing.

        MARCELLUS Horatio says 'tis but our fantasy,
        And will not let belief take hold of him
        Touching this dreaded sight twice seen of us:
        Therefore I have entreated him along
        With us to watch the minutes of this night,
        That if again this apparition come,
        He may approve our eyes and speak to it.

        HORATIO Tush, tush, 'twill not appear.

        BARNARDO Sit down awhile,
        And let us once again assail your ears,
        That are so fortified against our story,
        What we two nights have seen.

        HORATIO Well, sit we down,
        And let us hear Barnardo speak of this.

        BARNARDO Last night of all,
        When yond same star that's westward from the pole
        Had made his course t'illume that part of heaven
        Where now it burns, Marcellus and myself,
        The bell then beating one-

        MARCELLUS Peace, break thee off.
"""
            ),

    "gaiman": StyleTransfer(
        name="Neil Gaiman",
        
        description="""Neil Gaiman’s writing style is as distinctive as his imaginative storyscapes, characterized by its accessibility and a poetic, sometimes whimsical tone that belies the depth and darkness of his narratives. Gaiman’s prose often dances on the edge of the lyrical, weaving a rhythm that pulls readers along with a gentle but firm grip. His skill lies in crafting sentences that are both simple and profound, often employing a conversational tone that makes even the most fantastical elements feel intimately relatable.

        Gaiman’s use of language is deliberately measured; he chooses words with care, aiming for clarity and resonance rather than complexity. This is not to say his writing lacks sophistication. Rather, he achieves a certain elegance through the economy of his language, making each word work multiple layers of meaning and emotion. This technique is particularly effective in his ability to create atmosphere, a crucial element in the genres of fantasy and horror where setting often plays a critical role.

        Narrative structure in Gaiman’s work frequently involves multiple timelines or perspectives, yet he manages these complexities in a way that is seamless to the reader, often using a framing device or a storyteller character to provide cohesion. This approach not only adds depth to his stories but also pays homage to the oral storytelling traditions that influence much of his work.

        Dialogue in Gaiman’s books is another element that showcases his stylistic flair. He has a unique ability to capture voices distinctly, whether he’s writing for gods or mortals, children or monsters. The authenticity of these voices lends credibility to his worlds, no matter how outlandish they may be.

        In examining Gaiman’s work, one sees a writer who is both a master of his craft and a devotee of the story. He respects the power of words and wields them with a precision that makes his narratives fly off the page, straight into the vivid imaginations of his readers.""",
        
        example="""Shadow had done three years in prison. He was big enough and looked don't-fuck-with-me enough that his biggest problem was killing time. So he kept himself in shape, and taught himself coin tricks, and thought a lot about how much he loved his wife.

        The best thing—in Shadow's opinion, perhaps the only good thing—about being in prison was a feeling of relief. The feeling that he'd plunged as low as he could plunge and he'd hit bottom. He didn't worry that the man was going to get him, because the man had got him. He was no longer scared of what tomorrow might bring, because yesterday had brought it.

        It did not matter, Shadow decided, if you had done what you had been convicted of or not. In his experience everyone he met in prison was aggrieved about something: there was always something the authorities had got wrong, something they said you did when you didn't—or you didn't do quite like they said you did. What was important was that they had gotten you.

        He had noticed it in the first few days, when everything, from the slang to the bad food, was new. Despite the misery and the utter skin-crawling horror of incarceration, he was breathing relief.

        Shadow tried not to talk too much. Somewhere around the middle of year two he mentioned his theory to Low Key Lyesmith, his cellmate.

        Low Key, who was a grifter from Minnesota, smiled his scarred smile. "Yeah," he said. "That's true. It's even better when you've been sentenced to death. That's when you remember the jokes about the guys who kicked their boots off as the noose flipped around their necks, because their friends always told them they'd die with their boots on."

        "Is that a joke?" asked Shadow.

        "Damn right. Gallows humor. Best kind there is."

        "When did they last hang a man in this state?" asked Shadow.

        "How the hell should I know?" Lyesmith kept his orange-blond hair pretty much shaved. You could see the lines of his skull. "Tell you what, though. This country started going to hell when they stopped hanging folks. No gallows dirt. No gallows deals."

        Shadow shrugged. He could see nothing romantic in a death sentence.

        If you didn't have a death sentence, he decided, then prison was, at best, only a temporary reprieve from life, for two reasons. First, life creeps back into prison. There are always places to go further down. Life goes on. And second, if you just hang in there, someday they're going to have to let you out.

        In the beginning it was too far away for Shadow to focus on. Then it became a distant beam of hope, and he learned how to tell himself "this too shall pass" when the prison shit went down, as prison shit always did. One day the magic door would open and he'd walk through it. So he marked off the days on his Songbirds of North America calendar, which was the only calendar they sold in the prison commissary, and the sun went down and he didn't see it and the sun came up and he didn't see it. He practiced coin tricks from a book he found in the wasteland of the prison library; and he worked out; and he made lists in his head of what he'd do when he got out of prison.

        Shadow's lists got shorter and shorter. After two years he had it down to three things."""
    ),

    "stephen_king": StyleTransfer(
        name="Stephen King",
        
        description="""Stephen King’s writing style is often described as direct and vivid, with a strong narrative voice that pulls readers into his stories. His approach is characterized by an accessible, conversational tone that makes even the most fantastical elements seem believable. King has a knack for creating realistic dialogue and richly detailed settings, which are instrumental in building suspense and horror.

        King’s sentence structure varies widely to suit the pacing of his narrative. In tense scenes, he employs short, choppy sentences to ramp up the suspense. Conversely, when developing characters or setting a scene, he uses longer, more descriptive sentences that allow readers to fully immerse themselves in the world he has created. This flexibility in sentence structure helps maintain a dynamic rhythm throughout his novels, keeping readers engaged from start to finish.

        One of King’s most notable techniques is his use of an active voice, which lends immediacy and intimacy to his storytelling. This choice helps to create a sense of urgency and draws readers closer to the characters’ experiences. Additionally, King often employs adverbs and adjectives sparingly, choosing instead strong, vivid verbs that convey action and emotion effectively. This not only tightens his prose but also enhances the visual imagery in his writing.

        King’s use of foreshadowing and flashback is also adept, weaving complex narratives that span different times and perspectives. These elements are not just stylistic; they are integral to unfolding the multilayered plots for which he is known. This narrative complexity, combined with his straightforward prose, allows King to explore deep, often dark themes without losing his audience.

        Stephen King’s writing style is a blend of straightforward narrative, vivid description, and careful pacing. His ability to balance detailed character development with gripping plotlines is what has made him a master of modern American literature, particularly in the horror genre. His style is both accessible and engaging, explaining his enduring popularity and influence.""",
        
        example="""Something new had happened. For the first time in forever, something new. Before the universe there had been only two things. One was Itself and the other was the Turtle. The Turtle was a stupid old thing that never came out of its shell. It thought that maybe the Turtle was dead, had been dead for the last billion years or so. Even if it wasn't, it was still a stupid old thing, and even if the Turtle had vomited the universe out whole, that didn't change the fact of its stupidity. It had come here long after the Turtle withdrew into its shell, here to Earth, and It had discovered a depth of imagination here that was almost new, almost of concern. This quality of imagination made the food very rich. Its teeth rent flesh gone stiff with exotic terrors and voluptuous fears: they dreamed of nightbeasts and moving muds; against their will they contemplated endless gulphs. Upon this rich food It existed in a simple cycle of waking to eat and sleeping to dream. It had created a place in Its own image, and It looked upon this place with favor from the deadlights which were Its eyes. Derry was Its killing-pen, the people of Derry Its sheep. Things had gone on. Then . . . these children. Something new. For the first time in forever. When It had burst up into the house on Neibolt Street, meaning to kill them all, vaguely uneasy that It had not been able to do so already (and surely that unease had been the first new thing), something had happened which was totally unexpected, utterly unthought of, and there had been pain, pain, great roaring pain all through the shape it had taken, and for one moment there had also been fear, because the only thing It had in common with the stupid old Turtle and the cosmology of the macroverse outside the puny egg of this universe was just this: all living things must abide by the laws of the shape they inhabit. For the first time It realized that perhaps Its ability to change Its shapes might work against It as well as for It. There had never been pain before, there had never been fear before, and for a moment It had thought It might die — oh Its head had been filled with a great white silver pain, and it had roared and mewled and bellowed and somehow the children had escaped. But now they were coming. They had entered Its domain under the city, seven foolish children blundering through the darkness without lights or weapons. It would kill them now, surely. It had made a great self -discovery: It did not want change or surprise. It did not want new things, ever. It wanted only to eat and sleep and dream and eat again. Following the pain and that brief bright fear, another new emotion had arisen (as all genuine emotions were new to It, although It was a great mocker of emotions): anger. It would kill the children because they had, by some amazing accident, hurt It. But It would make them suffer first because for one brief moment they had made It fear them. Come to me then, It thought, listening to their approach. Come to me, children, and see how we float down here . . . how we all float. And yet there was a thought that insinuated itself no matter how strongly It tried to push the thought away. It was simply this: if all things flowed from It (as they surely had done since the Turtle sicked up the universe and then fainted inside its shell), how could any creature of this or any other world fool It or hurt It, no matter how briefly or triflingly? How was that possible? And so a last new thing had come to It, this not an emotion but a cold speculation: suppose It had not been alone, as It had always believed? Suppose there was Another? And suppose further that these children were agents of that Other? Suppose . . . suppose . . . It began to tremble. Hate was new. Hun was new. Being crossed in Its purpose was new. But the most terrible new thing was this fear. Not fear of the children, that had passed, but the fear of not being alone. No. There was no other. Surely there was not. Perhaps because they were children their imaginations had a certain raw power It had briefly underestimated. But now that they were coming, It would let them come. They would come and It would cast them one by one into the macroverse . . . into the deadlights of Its eyes. Yes. When they got here It would cast them, shrieking and insane, into the deadlights."""
    ), 

    "agatha_christie": StyleTransfer(
        name="Agatha Christie",

        description="""Agatha Christie, the undisputed queen of mystery, has captivated millions with her intricate plots and memorable characters. Yet, it is her distinctive writing style that subtly hooks the reader, weaving complex narratives with clarity and deceptive simplicity. Christie’s prose is accessible and straightforward, eschewing ornate language for functional and direct expressions that drive the story forward and keep readers deeply engaged.

        Christie’s narrative technique often involves an omniscient point of view, which allows her to present the thoughts and feelings of multiple characters. This broad perspective is crucial for the mystery genre, as it lets her distribute or withhold information to build suspense and intrigue. Her use of dialogue is particularly effective; conversations between characters are not just vehicles for character development but are also essential in laying out red herrings and clues. This dialogue-driven approach helps maintain a brisk pace and makes her novels compulsively readable.

        In terms of sentence structure, Christie favored balance and rhythm. Her sentences are predominantly compound or complex, which helps in layering information and ideas seamlessly. This structure is particularly effective in mystery writing, where the timing of revelations is key to maintaining suspense. Christie’s adept use of this technique allows her to keep readers guessing, leading them through a maze of plot twists and turns without losing them along the way.

        Christie’s choice of vocabulary is deliberately restrained. She avoids unnecessary jargon or overly technical terms that might distract from the narrative. This simplicity ensures that the focus remains on the plot and characters, making her books accessible to a wide audience. Her ability to say much with little, to hint rather than show, and to leave space for the reader’s imagination is a hallmark of her style. This subtlety extends to her use of adjectives and adverbs, which are employed sparingly; Christie relies more on strong verbs and precise nouns to create vivid scenes and convey action, keeping the reader’s attention fixed firmly on the unfolding mystery.""",

        example="""The intense interest aroused in the public by what was known at the time as “The Styles Case” has now somewhat subsided. Nevertheless, in view of the world-wide notoriety which attended it, I have been asked, both by my friend Poirot and the family themselves, to write an account of the whole story. This, we trust, will effectually silence the sensational rumours which still persist.

        I will therefore briefly set down the circumstances which led to my being connected with the affair.

        I had been invalided home from the Front; and, after spending some months in a rather depressing Convalescent Home, was given a month’s sick leave. Having no near relations or friends, I was trying to make up my mind what to do, when I ran across John Cavendish. I had seen very little of him for some years. Indeed, I had never known him particularly well. He was a good fifteen years my senior, for one thing, though he hardly looked his forty-five years. As a boy, though, I had often stayed at Styles, his mother’s place in Essex.

        We had a good yarn about old times, and it ended in his inviting me down to Styles to spend my leave there.

        “The mater will be delighted to see you again—after all those years,” he added.

        “Your mother keeps well?” I asked.

        “Oh, yes. I suppose you know that she has married again?”

        I am afraid I showed my surprise rather plainly. Mrs. Cavendish, who had married John’s father when he was a widower with two sons, had been a handsome woman of middle-age as I remembered her. She certainly could not be a day less than seventy now. I recalled her as an energetic, autocratic personality, somewhat inclined to charitable and social notoriety, with a fondness for opening bazaars and playing the Lady Bountiful. She was a most generous woman, and possessed a considerable fortune of her own."""
    ),

    "tolkien": StyleTransfer(
        name="J.R.R. Tolkien",

        description="""J. R. R. Tolkien’s writing style is as intricate and richly woven as the worlds he creates. His prose is characterized by a meticulous attention to detail and a profound reverence for language, which is evident in every sentence he crafts. Tolkien, a philologist by profession, had a deep understanding of language roots and structure, which he employed to construct the elaborate languages and names within his works, adding a layer of authenticity and depth to his storytelling.

        Tolkien’s narrative technique often involves an interplay of various linguistic styles, including archaic terms and structures, which evoke a sense of antiquity and legend. This is particularly evident in “The Lord of the Rings” and “The Silmarillion,” where he uses a formal, elevated diction reminiscent of epic poetry. This choice not only enriches the narrative but also aligns with the epic scope and high stakes of his stories. His sentences are typically long and descriptive, with lush, vivid descriptions that engage all the senses, inviting readers to fully immerse themselves in the world he has created.

        In constructing his narratives, Tolkien favors a slow build-up, allowing for extensive world-building and character development. This methodical pacing can be seen as a double-edged sword; while it serves to deeply draw the reader into the intricate details of Middle-earth, it also demands patience from the reader as the plot gradually unfolds. The use of detailed appendices and footnotes to explain the backstory and lore further exemplifies his thorough approach.

        Dialogue in Tolkien’s works often serves multiple functions—revealing character, advancing the plot, and enriching the world lore. He skillfully varies the speech patterns of his characters according to their origins and status, adding layers of realism and diversity to his character portrayals.

        Tolkien’s style, with its blend of ancient lore and rich linguistic tapestry, invites readers into a deeply immersive experience, reflecting his own deep connections to the myths and languages that inspired him. His writing not only tells a story but also evokes the feeling of reading a long-lost historical document, a testament to a past that, while fictional, feels profoundly real and tangible.""", 

        example="""They got up and withdrew quietly into the shadows, and made for the doors. Sam they left behind, fast asleep still with a smile on his face. In spite of his delight in Bilbo's company Frodo felt a tug of regret as they passed out of the Hall of Fire. Even as they stepped over the threshold a single clear voice rose in song.

        A Elbereth Gilthoniel,
        silivren penna míriel
        o menel aglar elenath!
        Na-chaered palan-díriel
        o galadhremmin ennorath,
        Fanuilos, le linnathon
        nef aear, sí nef aearon!

        Frodo halted for a moment, looking back. Elrond was in his chair and the fire was on his face like summer-light upon the trees. Near him sat the Lady Arwen. To his surprise Frodo saw that Aragorn stood beside her; his dark cloak was thrown back, and he seemed to be clad in elven-mail, and a star shone on his breast. They spoke together, and then suddenly it seemed to Frodo that Arwen turned towards him, and the light of her eyes fell on him from afar and pierced his heart.

        He stood still enchanted, while the sweet syllables of the elvish song fell like clear jewels of blended word and melody. 'It is a song to Elbereth,' said Bilbo. 'They will sing that, and other songs of the Blessed Realm, many times tonight. Come on!'"""
    ),

    "lovecraft": StyleTransfer(
        name="H.P. Lovecraft",  

        description="""H. P. Lovecraft’s writing style is a fascinating study in the use of atmospheric detail and complex sentence structures to evoke a sense of dread and the uncanny. His prose often leans towards the archaic, reflecting his admiration for 18th-century British writers. This choice of language not only sets a particular mood but also distances the reader from the familiar, everyday world, enhancing the eerie and otherworldly themes that dominate his work.

        Lovecraft’s sentences are typically long and elaborately structured, featuring multiple clauses and extensive use of commas, which guide the reader through a detailed, unfolding narrative. This labyrinthine sentence structure contributes to the creation of a dense, immersive world. It demands careful reading, pulling the reader deeper into the unsettling environments Lovecraft crafts. His adjectives are meticulously chosen to stir the imagination; words like “eldritch,” “decadent,” and “nocturnal” recur, painting his scenes with a brush of foreboding and mystery.

        The rhythm of Lovecraft’s writing also plays a crucial role in building suspense and horror. He frequently employs a technique of gradual revelation, where the true nature of the horror is obscured at the beginning and slowly unveiled through hints and implications. This method keeps the reader in a state of anticipation and allows Lovecraft to control the pace of the narrative, often culminating in a climactic revelation.

        Narrative structure in Lovecraft’s work often follows a first-person perspective, which serves to provide a direct, personal account of the horrors described. This perspective is crucial in making the unbelievable believable, as the protagonist’s descent into madness or confrontation with the incomprehensible seems more immediate and visceral.

        Lovecraft’s style is a blend of ornate descriptions, complex syntax, and a carefully modulated pace, all serving his themes of cosmic horror and mankind’s insignificant place in the universe. His distinctive approach not only defines the genre of cosmic horror but also profoundly influences how horror is written and experienced today.""",

        example="""I am forced into speech because men of science have refused to follow my advice without knowing why. It is altogether against my will that I tell my reasons for opposing this contemplated invasion of the antarctic with its vast fossil-hunt and its wholesale boring and melting of the ancient ice-cap and I am the more reluctant because my warning may be in vain. Doubt of the real facts, as I must reveal them, is inevitable; yet if I suppressed what will seem extravagant and incredible there would be nothing left. The hitherto withheld photographs, both ordinary and a‘rial, will count in my favour; for they are damnably vivid and graphic. Still, they will be doubted because of the great lengths to which clever fakery can be carried. The ink drawings, of course, will be jeered at as obvious impostures; notwithstanding a strangeness of technique which art experts ought to remark and puzzle over. In the end I must rely on the judgment and standing of the few scientific leaders who have, on the one hand, sufficient independence of thought to weigh my data on its own hideously convincing merits or in the light of certain primordial and highly baffling myth-cycles; and on the other hand, sufficient influence to deter the exploring world in general from any rash and overambitious programme in the region of those mountains of madness. It is an unfortunate fact that relatively obscure men like myself and my associates, connected only with a small university, have little chance of making an impression where matters of a wildly bizarre or highly controversial nature are concerned. It is further against us that we are not, in the strictest sense, specialists in the fields which came primarily to be concerned."""       
    ),

}