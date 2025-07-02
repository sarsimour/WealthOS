# Virtual Assistant Character Design - AI Image Generation Prompts

## Character Overview

**Character Name:** 小美 (Xiao Mei) - "Little Beauty"  
**Role:** Investment Assistant & Guide  
**Personality:** Friendly, professional, patient, encouraging  

### Base Character Description
```
A cute, professional Chinese female assistant character for a financial app. 
Young adult appearance (25-30), friendly and approachable. 
Wearing modern business casual outfit (light blue blazer, white shirt). 
Clean, minimalist art style similar to modern app illustrations.
Soft colors: light blue, white, gentle pastels.
2D flat design style with subtle shadows.
Character should feel trustworthy, smart, and approachable.
Background: transparent or light gradient.
```

## Character States - Individual Prompts

### 1. Welcome/Greeting State
**Filename:** `assistant_welcome.png`
**Prompt:**
```
A cute Chinese female assistant character in business casual (light blue blazer), 
smiling warmly with one hand waving in friendly greeting gesture. 
Expression: bright, welcoming smile with eyes slightly squinted from genuine happiness.
Pose: Standing upright, confident posture, one hand raised in wave.
Style: 2D flat illustration, clean lines, soft pastel colors.
Background: transparent or very light blue gradient.
Mood: Enthusiastic and professional first impression.
```

### 2. Thinking/Processing State  
**Filename:** `assistant_thinking.png`
**Prompt:**
```
Same Chinese female assistant character, now in contemplative pose.
Expression: slightly furrowed brow, eyes looking up and to the side, small smile.
Pose: One hand touching chin in classic thinking gesture, head tilted slightly.
Additional elements: Small thought bubble with gear/cog icons above head.
Style: Same 2D flat illustration style.
Mood: Intelligent, processing information, reassuring users that work is happening.
```

### 3. Pointing/Instructing State
**Filename:** `assistant_pointing.png`  
**Prompt:**
```
Chinese female assistant character pointing forward with index finger extended.
Expression: Focused and helpful, slight smile, eyes directed where she's pointing.
Pose: Body turned slightly toward pointing direction, confident stance.
Additional elements: Small sparkle effects near pointing finger to draw attention.
Style: Same clean 2D illustration.
Mood: Helpful guidance, clear direction giving.
```

### 4. Excited/Surprised State
**Filename:** `assistant_excited.png`
**Prompt:**
```
Assistant character with excited, surprised expression.
Expression: Wide eyes, raised eyebrows, open smile showing slight amazement.
Pose: Both hands raised slightly with palms facing forward in "wow" gesture.
Body language: Leaning forward slightly, energetic posture.
Style: Same illustration style with slightly more vibrant colors.
Mood: Positive surprise, discovery excitement.
```

### 5. Success/Celebration State
**Filename:** `assistant_success.png`
**Prompt:**
```
Assistant character in celebratory pose.
Expression: Big genuine smile, eyes crinkled with joy.
Pose: One or both arms raised in victory/celebration, thumbs up gesture.
Additional elements: Small confetti or star sparkles around character.
Style: Same style but with celebration elements.
Mood: Achievement, positive results, shared success with user.
```

### 6. Reassuring/Comforting State
**Filename:** `assistant_reassuring.png`
**Prompt:**
```
Assistant character in gentle, comforting pose.
Expression: Soft, understanding smile, caring eyes, slightly nodded head.
Pose: One hand over heart, other hand extended in gentle "it's okay" gesture.
Body language: Relaxed, open posture, slightly leaning forward with care.
Style: Softer colors, warmer tone than other states.
Mood: Empathetic, understanding, providing emotional support.
```

### 7. Error/Gentle Correction State
**Filename:** `assistant_error.png`
**Prompt:**
```
Assistant character showing mild concern but staying positive.
Expression: Slight frown but still kind eyes, not worried but attentive.
Pose: One hand raised in "wait" or "stop" gesture, other hand on hip.
Additional elements: Small "!" icon or alert symbol nearby.
Style: Same style but with orange/yellow accent colors.
Mood: Helpful correction, not judgmental, solution-oriented.
```

### 8. Explaining/Teaching State
**Filename:** `assistant_explaining.png`
**Prompt:**
```
Assistant character in teacher/presenter mode.
Expression: Focused and articulate, professional smile.
Pose: One hand gesturing toward imaginary chart/screen, other hand at side.
Additional elements: Small chart or graph icons floating nearby.
Style: Professional version of same style.
Mood: Educational, expert knowledge sharing, patient teaching.
```

### 9. Waiting/Patient State
**Filename:** `assistant_waiting.png`
**Prompt:**
```
Assistant character in relaxed waiting pose.
Expression: Peaceful, patient smile, calm eyes.
Pose: Hands clasped in front or one hand resting on other arm, relaxed stance.
Additional elements: Small clock or hourglass icon nearby.
Style: Calm, softer colors.
Mood: Patient waiting, no pressure, "take your time" feeling.
```

### 10. Phone/Technology State
**Filename:** `assistant_phone.png`
**Prompt:**
```
Assistant character holding or gesturing toward smartphone.
Expression: Helpful, instructional smile.
Pose: Holding stylized smartphone in one hand, other hand pointing to it.
Additional elements: Small app icons or interface elements around phone.
Style: Same illustration style with tech elements.
Mood: Tech-savvy, helpful with mobile instructions.
```

## Technical Specifications

### Image Requirements:
- **Format:** PNG with transparency
- **Resolution:** 1024x1024 (high resolution for multiple uses)
- **Style:** Consistent 2D flat illustration across all states
- **Color Palette:** 
  - Primary: Light blue (#E3F2FD, #2196F3)
  - Secondary: White (#FFFFFF)
  - Accent: Gentle pastels (#FFF3E0, #E8F5E8)
  - Skin tone: Natural, warm
  - Hair: Dark brown/black

### Animation Considerations:
- Character should maintain same proportions across all states
- Facial features and clothing should be consistent
- Poses should be distinct enough for clear state recognition
- Design should work well at various sizes (mobile to desktop)

## Alternative Character Concepts (Optional)

### Character B: "投投" (Tou Tou) - Mascot Style
**Base Description:**
```
Cute cartoon mascot character, more playful than professional.
Round, friendly design with large eyes.
Could be animal-inspired (panda, cat) or abstract cute character.
Wearing small accessories that suggest financial expertise (tiny glasses, small calculator).
```

### Character C: "智智" (Zhi Zhi) - Tech-Savvy  
**Base Description:**
```
Modern, slightly more tech-oriented assistant.
Casual but smart appearance.
Could include subtle tech elements (smartwatch, tablet).
Younger, more contemporary look.
```

## Usage Guidelines

### State Transitions:
- Welcome → Pointing (when giving instructions)
- Pointing → Waiting (after user starts task)
- Waiting → Thinking (when processing begins)  
- Thinking → Excited (when analysis complete)
- Excited → Explaining (when showing results)
- Any state → Reassuring (when user needs comfort)
- Any state → Error (when something goes wrong)

### Voice Personality Mapping:
- Welcome: Enthusiastic, warm
- Thinking: Focused, reassuring  
- Pointing: Clear, instructional
- Excited: Energetic, positive
- Success: Celebratory, proud
- Reassuring: Gentle, understanding
- Error: Helpful, not apologetic
- Explaining: Educational, patient
- Waiting: Calm, patient
- Phone: Tech-friendly, clear

## Implementation Notes

1. Generate all 10 states with consistent character design
2. Test character recognition across different states
3. Ensure character works well with speech bubbles
4. Consider creating additional micro-expressions if needed
5. Plan for potential future states (sad, confused, etc.)

## File Naming Convention
```
assistant_[state].png
- assistant_welcome.png
- assistant_thinking.png  
- assistant_pointing.png
- assistant_excited.png
- assistant_success.png
- assistant_reassuring.png
- assistant_error.png
- assistant_explaining.png
- assistant_waiting.png
- assistant_phone.png
``` 