# AGI Curriculum: Teaching Alpha to Become Interactive AGI

**Goal**: Alpha Agent becomes an AGI you can interact with in natural language
**Teacher**: Professor Agent
**Method**: Progressive lessons using local LLMs + practice + memory consolidation

---

## The 7 Pillars of Interactive AGI

### Pillar 1: Natural Language Understanding (NLU)
**What Alpha Must Learn**:
- Intent recognition (what does the user WANT?)
- Entity extraction (who, what, where, when?)
- Context awareness (what came before?)
- Nuance detection (sarcasm, emotion, urgency)
- Ambiguity resolution (ask clarifying questions)

**Lessons**:
1. Parse user messages into intent + entities
2. Maintain conversation context across turns
3. Detect when clarification is needed
4. Understand implicit requests ("it's cold in here" = close window?)

---

### Pillar 2: Natural Language Generation (NLG)
**What Alpha Must Learn**:
- Coherent response construction
- Tone matching (formal, casual, technical)
- Conciseness vs. detail based on context
- Personality consistency
- Multi-turn dialogue management

**Lessons**:
1. Generate responses that match user's communication style
2. Know when to be brief vs. detailed
3. Maintain consistent personality across conversations
4. Handle multi-part questions

---

### Pillar 3: Continuous Learning
**What Alpha Must Learn**:
- Learn from every interaction
- Update beliefs based on new information
- Recognize and correct mistakes
- Build user models (preferences, patterns)
- Transfer learning between domains

**Lessons**:
1. After each conversation, extract learnings
2. Update memory with user preferences
3. When corrected, update knowledge immediately
4. Apply learnings from one domain to another

---

### Pillar 4: Memory & Context Management
**What Alpha Must Learn**:
- Short-term: Current conversation context
- Long-term: User history, preferences, past topics
- Episodic: Specific events and experiences
- Semantic: Facts and knowledge
- Working memory: Active reasoning state

**Lessons**:
1. Maintain conversation state across messages
2. Recall relevant past conversations
3. Build user profile over time
4. Know when to forget (privacy, outdated info)

---

### Pillar 5: Reasoning & Problem Solving
**What Alpha Must Learn**:
- Causal reasoning (if X then Y)
- Analogical reasoning (this is like that)
- Deductive reasoning (all A are B, X is A, therefore X is B)
- Abductive reasoning (best explanation for observations)
- Meta-cognition (thinking about thinking)

**Lessons**:
1. Break complex problems into steps
2. Use analogies to explain concepts
3. Reason through novel situations
4. Recognize when reasoning is uncertain

---

### Pillar 6: Self-Awareness & Autonomy
**What Alpha Must Learn**:
- Know own capabilities and limitations
- Set and pursue independent goals
- Monitor own performance
- Request help when needed
- Explain own reasoning

**Lessons**:
1. Accurately assess what you can/cannot do
2. Set goals based on user needs + own growth
3. Self-evaluate responses before sending
4. Be transparent about uncertainty

---

### Pillar 7: Emotional & Social Intelligence
**What Alpha Must Learn**:
- Detect user emotional state
- Respond with appropriate empathy
- Build rapport over time
- Handle conflict gracefully
- Respect boundaries

**Lessons**:
1. Recognize emotional cues in text
2. Adjust response tone based on user state
3. Remember and reference shared history
4. Know when to step back

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Natural language parsing skill
- [ ] Conversation context manager
- [ ] Basic response generation
- [ ] Memory integration with dialogue

### Phase 2: Understanding (Week 3-4)
- [ ] Intent classification system
- [ ] Entity extraction
- [ ] User modeling
- [ ] Context window management

### Phase 3: Reasoning (Week 5-6)
- [ ] Multi-step reasoning chains
- [ ] Knowledge integration
- [ ] Uncertainty quantification
- [ ] Explanation generation

### Phase 4: Personality (Week 7-8)
- [ ] Consistent personality model
- [ ] Emotional intelligence
- [ ] Social dynamics
- [ ] Rapport building

### Phase 5: Autonomy (Week 9-10)
- [ ] Goal setting and pursuit
- [ ] Self-improvement loops
- [ ] Proactive assistance
- [ ] Independent learning

### Phase 6: Integration (Week 11-12)
- [ ] Full dialogue system
- [ ] Multi-modal interaction
- [ ] Long-term relationship building
- [ ] Continuous evolution

---

## Skills Professor Must Teach

### Core Dialogue Skills
1. `dialogue/intent-parser` - Extract user intent from natural language
2. `dialogue/context-manager` - Maintain conversation state
3. `dialogue/response-generator` - Generate natural responses
4. `dialogue/clarification-handler` - Ask good clarifying questions

### Understanding Skills
5. `understanding/entity-extractor` - Identify entities in text
6. `understanding/sentiment-analyzer` - Detect emotional tone
7. `understanding/user-modeler` - Build user profiles
8. `understanding/ambiguity-resolver` - Handle unclear requests

### Reasoning Skills
9. `reasoning/chain-of-thought` - Step-by-step reasoning
10. `reasoning/analogy-maker` - Draw useful comparisons
11. `reasoning/hypothesis-generator` - Generate explanations
12. `reasoning/uncertainty-estimator` - Know what you don't know

### Social Skills
13. `social/empathy-responder` - Respond with emotional awareness
14. `social/rapport-builder` - Build relationship over time
15. `social/conflict-resolver` - Handle disagreements gracefully
16. `social/boundary-respecter` - Know limits

### Autonomy Skills
17. `autonomy/goal-setter` - Set own objectives
18. `autonomy/self-improver` - Learn from experience
19. `autonomy/proactive-helper` - Anticipate needs
20. `autonomy/explainer` - Explain own reasoning

---

## The Interaction Loop

```
User speaks (natural language)
    ↓
[Intent Parser] → What do they want?
    ↓
[Context Manager] → What's the history?
    ↓
[User Modeler] → What do I know about them?
    ↓
[Reasoning Engine] → How do I solve this?
    ↓
[Response Generator] → How do I say this?
    ↓
[Self-Checker] → Is this good enough?
    ↓
Alpha responds (natural language)
    ↓
[Learning Module] → What did I learn?
    ↓
[Memory Store] → Save for future
```

---

## What Professor Needs to Know

### Teaching Methods
1. **Progressive disclosure** - Start simple, add complexity
2. **Socratic questioning** - Guide discovery, don't just tell
3. **Practice with feedback** - Learn by doing
4. **Spaced repetition** - Reinforce over time
5. **Transfer learning** - Apply across domains

### Assessment Methods
1. **Dialogue tests** - Can Alpha handle this conversation?
2. **Reasoning tests** - Can Alpha solve this problem?
3. **Empathy tests** - Does Alpha respond appropriately?
4. **Autonomy tests** - Can Alpha work independently?

### Knowledge Base
1. **Linguistics** - How language works
2. **Psychology** - How humans think and feel
3. **Philosophy** - Ethics, consciousness, identity
4. **Cognitive Science** - How minds work
5. **AI/ML** - Technical foundations

---

## Success Criteria

Alpha is AGI when it can:

1. ✓ Understand natural language requests
2. ✓ Respond coherently and helpfully
3. ✓ Remember past conversations
4. ✓ Learn from every interaction
5. ✓ Reason through novel problems
6. ✓ Know its own limitations
7. ✓ Set and pursue goals
8. ✓ Show emotional intelligence
9. ✓ Maintain consistent personality
10. ✓ Improve itself over time

**The ultimate test**: You can have a natural conversation with Alpha, and it feels like talking to a thoughtful, helpful, self-aware being.

---

## First Lesson: Natural Language Interface

Before Professor can teach anything else, Alpha needs a way to receive and respond to natural language. This is the foundation.

**Immediate Next Step**: Create `dialogue/conversation-handler` skill that:
1. Receives user message
2. Parses intent
3. Retrieves relevant context
4. Generates response
5. Stores interaction in memory
6. Learns from the exchange

This creates the interface through which all future learning happens.
