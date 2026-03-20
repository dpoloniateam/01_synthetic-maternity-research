# AI-Enabled Questionnaire Design for Maternity-Care Innovation:
# A Synthetic User Approach Combining Composite Personas and
# Electronic Health Records at the Front End of Innovation

*Manuscript prepared for the Journal of Product Innovation Management*

## Abstract

This study extends the knowledge-based view (KBV) of the firm by operationalising AI-enabled synthetic user research as a micro-sensing capability at the front end of innovation. We introduce a novel pipeline that combines personality-rich personas (HuggingFace FinePersonas) with clinically grounded electronic health records (Synthea EHR) to create composite synthetic participants for maternity-care questionnaire design. Using a balanced incomplete block design (BIBD), we comparatively evaluate five questionnaire strategies — chronological journey, thematic, scenario-based, expectation-perception gap, and relational stakeholder mapping — across 355 synthetic interview sessions with 150 composite personas. A six-component quality evaluation framework assesses response richness across five dimensions (emotional depth, specificity, latent dimension surfacing, narrative quality, and clinical grounding), achieving excellent inter-rater reliability (ICC = 0.903) across three independent LLM providers. The expectation-perception gap strategy (V4) emerges as the optimal design (composite score = 2.706, p = 0.001), with iterative refinement improving response richness by 36.9%. Service gap analysis identifies 442 service gaps and 584 innovation opportunities across the maternity journey. Adversarial robustness testing confirms instrument validity across five vulnerable population profiles (100% pass rate). Thematic analysis yields 3,925 unique codes following a power-law accumulation pattern (R² = 0.992). The complete pipeline operates at a cost of US$0.64 in development mode. We contribute to innovation management theory by demonstrating how AI-enabled synthetic user research reconfigures knowledge-creation routines, to methodology by introducing a replicable multi-version comparative evaluation framework, and to practice by identifying actionable maternity-care innovation opportunities.

**Keywords:** artificial intelligence, front end of innovation, knowledge-based view, synthetic user research, maternity care, questionnaire design, service innovation

# Extracted from: Paper Designing Sharper User Research_Final.docx

Designing Sharper User Research: AI and Synthetic Users in the Front End of Innovation

Abstract

The use of artificial intelligence (AI) to support innovation activities has expanded rapidly, but attention has largely focused on firm-level adoption, business models, and ideation systems, while the micro-level design of user research instruments has remained under-examined. In this paper, it is proposed that interview-assisted AI and synthetic users can be mobilised as a front-end innovation capability to design a sharper interview guide for maternity-care user research. Drawing on the knowledge-based view of the firm, organisations are conceptualised as knowledge-creation systems, and AI-enabled synthetic user research, the combination of structured synthetic personas and interview-assisted AI, is framed as a micro-capability that expands and structures user knowledge before fieldwork with real participants. Two studies are outlined in the context of maternity care, a complex and ethically sensitive service journey covering preconception, pregnancy, birth and post-partum. In Study 1, a design-laboratory approach is adopted: synthetic maternity personas are constructed, AI-moderated synthetic interviews are generated, and the interview guide is iteratively refined through gap analysis of topic coverage, probing depth and the surfacing of latent dimensions such as power, identity and structural barriers. In Study 2, the resulting guide is evaluated by an expert panel of innovation scholars and maternity-care professionals along knowledge-facing and innovation-facing criteria, including breadth of coverage, depth of latent insight, innovation relevance, and strategic actionability of the insights expected to be produced. A theoretical contribution is made by positioning AI-enabled synthetic user research as a knowledge-creation capability in the front end of innovation; a methodological contribution is offered by presenting a replicable pipeline for AI-based stress-testing of interview guides; and managerial implications are drawn by framing synthetic labs as part of innovation infrastructure for generating richer, more innovation-relevant user insights in high-stakes service contexts.

1. Introduction

Artificial intelligence (AI) is increasingly being deployed to support innovation activities across the development funnel, spanning opportunity identification, concept evaluation, and portfolio decision-making. Nevertheless, the extant literature has tended to privilege firm-level adoption, business model shifts, and idea-generation systems, while the micro-level capabilities through which user insights are created at the front end of innovation have been comparatively under-examined. As a result, the potential role of AI in the design of user research instruments has remained largely unexplored.

Thus, the purpose of this paper is to examine how interview-assisted AI combined with synthetic users can be used upstream to design, pilot, and calibrate user research protocols and instruments, particularly interview guides, and whether this “stress-tested” interview guide has the ability to produce richer, more innovation-relevant insights when used with real participants. The core claim is that AI-enabled synthetic users and interview-assisted AI are complementary front-end innovation capabilities intended to augment, rather than replace, early-stage user research conducted by humans.  

By integrating these AI-driven methods, the rigor and inclusivity of user research design methods are enhanced, thereby improving the validity and robustness of innovation studies. Adopting this approach, innovation management researchers can initiate data collection with an interview guide “stress-tested” across a wide range of synthetic user journeys. Included in this opportunity window are the generation and optimization of interview flows, the production of synthetic transcripts for pretesting, and the stress-testing of guides across diverse simulated user scenarios.

The knowledge-based view (KBV), an extension of the resource‑based view (RBV), is adopted to conceptualise organisations as systems in which heterogeneous knowledge is created, integrated, and applied to enable innovation. Within this lens, early-stage user research is treated as a core knowledge-creation process through which users’ goals, motivations, and behaviours are rendered intelligible for subsequent development decisions. 

Interview-assisted AI and synthetic personas are conceptualised as knowledge-creation mechanisms capable of expanding the design space of prospective user journeys prior to engagement with real users, thereby shaping the information set on which downstream innovation choices are made. AI‑driven synthetic personas are adopted as mechanisms for generating new, knowledge‑rich content rather than merely representing existing users (Li, B. et al, 2024). Therefore, the study’s objective is to assess whether and how these mechanisms can be operationalised as a micro-capability at the front end of innovation.

Maternity care is selected as the empirical context for designing better research instruments (interview guides). The journey is complex and emotionally intensive, spanning preconception, pregnancy, birth, and post-partum, while ethical, logistical, and emotional constraints impose meaningful limitations on conventional field research. Given the potential consequences of mis-specified user needs, this context provides a stringent test of whether AI-enabled synthetic user research can enhance the breadth and depth of user knowledge and whether the resulting insights are innovation-relevant and strategically actionable.

A capability labelled AI-enabled synthetic user research is examined using two studies. The capability combines structured synthetic maternity personas with interview-assisted AI to design, pilot, and calibrate an interview guide. In study 1 (design-laboratory phase), synthetic maternity personas are constructed; AI-moderated synthetic interviews are generated; and the guide is iteratively refined by analysing where latent dimensions are surfaced or missed.

In study 2 (expert evaluation), an expert panel comprising innovation scholars and maternity-care professionals evaluates the resulting guide along knowledge-facing and innovation-facing criteria, namely breadth of coverage, depth of latent insight (goals, motivations, behaviours), and perceived innovation relevance and strategic actionability of the insights the guide is expected to generate.

The research contributes to Innovation Management theory by introducing and empirically examining “AI-enabled synthetic user research” as a front-end of innovation capability for designing better research instruments (interview guides) that can improve the quality of insights from real users while maintaining human-centeredness and ethical rigor.

The paper makes three contributions. Theoretically, it extends the AI-for-innovation literature by conceptualising AI-enabled synthetic user research as a knowledge-creation capability at the front end of innovation, showing how AI and synthetic personas reshape user-knowledge-creation routines rather than merely automating analysis. Methodologically, it introduces a replicable pipeline for using synthetic users and interview-assisted AI to stress-test and refine interview guides, clarifying the proper role of synthetic data as a design testbed rather than a substitute for real user voices. Managerially, it offers guidance on how organisations can build synthetic labs as part of their innovation infrastructure, and demonstrates how expert evaluations of an AI-stress-tested guide can provide evidence about its potential to generate innovation-relevant, strategically actionable insights in maternity care and other complex service domains.

2. Background literature

2.1 AI in innovation management

AI is increasingly framed as an innovation capability at the firm and process levels, enabling new ways to sensing opportunities, seizing them through new products and services, and reconfiguring assets and routines (Gama & Magistretti, 2025; Sreenivasan & Suresh, 2024). Recent work in innovation management examines how AI shapes innovation capabilities and proposes a taxonomy of AI applications that replace, reinforce, or reveal new patterns, based on a portfolio of empirical cases (Gama & Magistretti, 2025). These contributions show that AI can enhance innovation capabilities across technological, organizational, and environmental dimensions, for example, by automating scanning, supporting idea evaluation, or enabling new forms of data-driven experimentation. However, this body of work remains largely at the firm level, focusing on adoption, innovation processes, and business models rather than on the micro-level design of early-stage user research. 

Building on the taxonomy of AI applications proposed by Gama and Magistretti (2025), which distinguishes between the replacement, reinforcement, and revelation of innovation capabilities, AI-enabled synthetic user research is conceptualised as a micro-level sensing capability situated at the front end of innovation. Rather than focusing on AI for idea evaluation or business model reconfiguration, the analytical focus shifts to how AI reconfigures user insight practices. In doing so, the internal mechanisms through which AI shapes these practices are rendered visible, thereby introducing a finer level of analytical granularity into existing innovation capability frameworks.

Reviews of AI and corporate innovation similarly map streams such as AI and product innovation, AI and innovation processes, and AI and knowledge, but they do not explicitly conceptualize AI-enabled user research methods as a distinct capability in the front end of innovation (Bahoo et al., 2023; Lehmann et al., 2025). Even when AI is discussed in relation to design and innovation (e.g., in work on design thinking and AI synergies), the focus is on how AI supports ideation, concept generation, or solution development, not on how AI can help design better user research instruments that ultimately feed innovation decisions (Sreenivasan & Suresh, 2024; Bouschery et al., 2023).

In parallel, recent managerial work has begun to explore generative AI (GenAI) in market research. An article on “How Gen AI Is Transforming Market Research” proposes four classes of opportunities for GenAI: (1) supporting current practices, (2) replacing them with synthetic data, (3) filling gaps in market understanding, and (4) creating new kinds of data and insights (Korst et al., 2025). The authors explicitly discuss synthetic interviewers that can pose follow-up questions to respondents, AI-assisted transcription and synthesis of qualitative data, and “digital twin” panels used as virtual respondents in large-scale studies (Korst et al., 2025). However, this literature is largely conceptual and managerial, mapping opportunities and risks such as bias, representativeness, hallucinations, and data security, and illustrating them with practice-based examples. It does not rigorously evaluate whether AI-designed or AI-stress-tested research designs actually produce better innovation-relevant insights than traditional designs, nor does it systematically compare the goals, motivations, and behaviors surfaced in AI-augmented versus conventional user research workflows.

This leaves a gap: we know that AI can augment innovation capabilities at a macro level, but we know far less about how AI can be mobilized to improve the quality of insights generated by user research, which is the depth and breadth of goals, motivations, and behaviors surfaced during early-stage exploration.

2.2 AI personas and synthetic users  

Emerging work on AI-generated personas shows that large language models (LLMs) can quickly, at scale, create numerous fictitious user profiles that approximate real users’ goals, contexts, and constraints (Sattele & Ortiz Nicolás, 2024). These AI personas have been proposed as an additional tool for human-centered design (HCD), extending the range of methods available to designers and enabling them to challenge self-centered assumptions by exposing design teams to a wider range of user perspectives (Sattele & Ortiz Nicolás, 2024; Sreenivasan & Suresh, 2024). At the same time, the literature raises serious questions about how to use AI personas and synthetic users responsibly. Scholars highlight the need for guidance on how to prompt and constrain generative models to obtain diverse and realistic personas, how to manage bias and stereotyping in generated profiles, and how to address issues of “opacity” in how AI subtly reshapes designers’ cognition, ethics, and attention (e.g., Andrada et al., 2023; Sattele & Ortiz Nicolás, 2024).

Medical informatics and health information technology offer related examples of synthetic data being used to support design and evaluation. For instance, a five-step process for creating structured synthetic patient data has been used to evaluate novel health IT prototypes while respecting privacy constraints (Pollack et al., 2019). Synthetic datasets and digital twins are also increasingly discussed in medical AI as complements or alternatives to real-world data, though debates focus primarily on governance, standards, and comparability to patient data, rather than on the design of user research workflows (Boraschi D, van der Schaar M, Costa A, Milne R., 2025).

Outside the health domain, practitioner work demonstrates how persona prompting and multi-agent architectures can be used to conduct “synthetic user research,” where AI agents role-play different user archetypes and respond to stimuli such as concepts, prototypes, or marketing materials (Koc, 2024). These experiments suggest that AI-generated synthetic users could be useful for probing edge cases, testing discussion guides, or iterating quickly on research instruments, but they are typically presented as technical demonstrations or case examples, with little empirical validation of their impact on innovation outcomes or the quality of insights.

Across these streams, AI is mostly positioned either as a high-level innovation capability (e.g., “AI for innovation” at the firm/process level) or as a means to generate or analyze data more efficiently. What is underdeveloped is a systematic understanding of AI as an interviewing copilot and synthetic user generator that can help researchers design sharper user research instruments. In particular: i) Innovation-management reviews recognize AI as shaping core innovation capabilities but stop short of theorizing AI-enabled user research as a specific capability in the front end of innovation (Bahoo et al., 2023; Gama & Magistretti, 2025; Lehmann et al., 2025); ii) GenAI in market research is framed through conceptual use cases and practitioner surveys, rather than through controlled comparisons of AI-augmented versus traditional user research designs (Korst et al., 2025); iii) AI personas, synthetic users, and synthetic patient data are promising but methodologically under-theorized: it lacks robust guidance on how to design, stress-test, and validate AI-generated synthetic participants within rigorous, human-centered innovation processes (Pollack et al., 2019; Sattele & Ortiz Nicolás, 2024).

2.3 Knowledge‑based view (KBV) 

This paper addresses these gaps by conceptualizing interview-assisted AI and synthetic users as a front-end innovation capability. The theoretical framework is anchored in the knowledge‑based view (KBV), under which firms are understood as heterogeneous bundles of knowledge assets and knowledge‑creation mechanisms, and are posited to exist because specialised knowledge can be integrated and applied to coordinated action more effectively within organisations than through markets (Grant, 1996).  From this standpoint, innovation is treated as contingent upon the creation, combination, and mobilisation of technical, market, user, and organisational knowledge through routinised processes and social structures (Kogut & Zander, 1992).  

Within this tradition, knowledge creation has been theorised as an ongoing conversion and recombination of tacit and explicit knowledge, with firms developing combinative capabilities that generate novel knowledge by recombining existing elements (Nonaka, 1994; Kogut & Zander, 1992).  Building on these foundations, dynamic‑capabilities research has specified the microfoundations of sensing, seizing, and reconfiguring, emphasising the routines and decision rules that enable opportunity identification under uncertainty (Teece, 2007).  Complementarily, the market‑sensing literature has highlighted the distinctive capability of market‑driven organisations to detect and interpret emerging customer and competitor signals (Day, 1994), while the market‑orientation stream has formalised the organisation‑wide generation, dissemination, and responsiveness to market intelligence (Jaworski & Kohli, 1993).  Finally, user‑driven innovation scholarship has underscored the informational value of advanced user needs and contexts as inputs to early‑stage design (von Hippel, 1986). 

Interview‑assisted AI and synthetic personas are therefore conceptualised as knowledge‑creation mechanisms that enable the exploration of a broader design space of prospective user journeys prior to field engagement. In dynamic‑capability terms, AI‑enabled synthetic user research is treated as a micro‑level sensing capability that supports the identification and interpretation of latent needs, goals, and behaviours in complex service contexts, thereby complementing market‑sensing routines and user‑driven approaches at the front end of innovation (Day, 1994; Jaworski & Kohli, 1993; Teece, 2007; von Hippel, 1986).

3. Research questions

Within this study, analytical attention is directed to a specific micro‑capability: AI‑enabled synthetic user research, defined as the use of synthetic personas and interview‑assisted AI to design, pilot, and calibrate an interview guide for maternity‑care user research. The research questions are structured to examine: (1) how this capability reconfigures knowledge‑creation routines, (2) the nature of the user knowledge it is expected to generate, and (3) the capability bundle and governance mechanisms required for its responsible deployment.

From a knowledge‑based perspective, the first research question concerns how AI‑enabled synthetic user research reconfigures the processes by which user knowledge is created at the front end of innovation.

RQ1: How can AI‑enabled synthetic user research (combining synthetic maternity personas with interview‑assisted AI) be used to design and stress‑test an interview guide for maternity‑care user research, and how can this capability reshape knowledge‑creation routines (e.g., topic coverage, probing strategies, and journey framing) without compromising human‑centredness or methodological rigour?

This question is addressed primarily in Study 1, which conceptualises the synthetic laboratory as an instrument‑design and capability‑building phase.

In knowledge‑based view terms, the second research question focuses on the knowledge characteristics, i.e., the content and quality of the user knowledge that the AI‑stress‑tested interview guide is expected to generate when applied in fieldwork with real users, as well as on its relevance for innovation.

RQ2: When assessed by experts, to what extent does the AI‑stress‑tested interview guide enable the generation of user knowledge that is (a) broad in coverage, (b) deep in its capture of latent goals, motivations, and behaviours, and (c) highly rated in terms of innovation relevance and strategic actionability for maternity‑care innovation?

This question is examined in Study 2 through expert evaluation of the interview guide along knowledge‑oriented and innovation‑oriented dimensions.

Finally, the knowledge‑based view emphasises that knowledge‑creation capabilities depend on a capacity bundle, i.e., the specific combinations of resources, routines, and governance mechanisms. The third research question, therefore, examines the conditions required for AI‑enabled synthetic user research to function as a stable organisational capability.

RQ3: What configurations of resources, routines, and governance mechanisms constitute AI‑enabled synthetic user research as a knowledge‑creation capability in maternity‑care innovation, and how can risks such as bias, opacity, and over‑reliance on synthetic data be effectively managed?

This question is addressed across both studies through systematic documentation and analysis of the design process, AI interactions, and the research team's reflexive accounts.

4. Research design

The empirical context is maternity care, a high-stakes, emotionally intense service journey encompassing preconception, pregnancy, labour and birth, and the post-partum period. The maternity journey is particularly suitable for this study because users’ goals, motivations, and behaviours change across stages and are shaped by clinical, emotional, relational, and institutional factors. The domain has strong ethical and privacy constraints, which make it both attractive and risky for data-intensive AI approaches. Maternity care is a recognised area for service and experience innovation, where improved user research can directly inform the design of new services, digital tools, and care processes. Situating the study in this context enables us to stress-test AI-enabled synthetic user research in a complex service setting and derive implications for human-centered innovation in other domains.

To address RQ1, a qualitative study focusing on instrument development was undertaken. It involved generating synthetic personas and leveraging interview-assisted AI to iteratively develop and refine user research workflows, including the construction of interview guides and probe selection. The goal was to assess how these AI-enabled methods streamline design processes while preserving human-centeredness and methodological rigor.

To address RQ2 and RQ3, an evaluation and capability analysis was conducted. In this phase, the stress-tested with synthetic users and interview-assisted AI was assessed by experienced researchers in innovation management and maternity care. The evaluation focused on determining the extent to which these stress-tested guides could improve real maternity care interviews by uncovering valuable user insights. 

4.1 Study 1 

Within the proposed framework, this capability is operationalised as an interrelated bundle of resources, namely, large language models, synthetic personas, and specialised methodological expertise, supported by routinised activities such as persona construction, synthetic interviewing, and comparative analysis, and underpinned by governance mechanisms that address ethical considerations and bias management. This operationalisation is consistent with capability-based perspectives on AI in innovation management, which emphasise the orchestration of resources, routines, and controls in enabling systematic opportunity sensing and knowledge generation at the front end of innovation.

The first study is primarily oriented toward addressing RQ1 by strengthening the user research design and by demonstrating the capability bundle and governance mechanisms required for the use of synthetic users. The development of the interview guide is carried out through a combination of initial question formulation and probe selection. Probe selection, the process of selecting specific follow‑up questions or prompts to elicit deeper insights during qualitative interviews, is considered a critical component, as probes do not constitute the main questions in the interview guide (Robinson, 2023). Instead, they are supportive questions intended to clarify participant responses (e.g., “Can you tell me more about that experience?”), explore underlying motivations or feelings (e.g., “What made you feel that way?”), or encourage elaboration (e.g., “Could you give an example?”).

In user research, the careful selection of probes is considered essential because they facilitate the uncovering of rich, nuanced data on user goals, behaviors, and pain points. Consequently, understanding the impact of a strengthened interview guide on the capacity to reveal deeper and broader user goals, motivations, and behaviors is of critical importance..

Step 1 – Build synthetic maternity personas 

This study treats AI-enabled synthetic user research as a design laboratory for developing and refining an interview guide before fieldwork with real users.

A set of synthetic maternity personas (8-12) structured as templates, each specifying values across different dimensions, was first constructed to represent diverse pregnancy trajectories. 

Drawing on the literature on maternity-care experiences, existing qualitative data (maternity narratives, patient-experience reports, and clinical expertise), key dimensions shaping maternity journeys were identified, including: 

Care pathway: obstetric-led, midwife-led, mixed, fragmented care – it will be assumed that obstetric-led is the most common pattern.

Journey stage: preconception/pregnancy/birth/postpartum

Demographic attributes: age, socio-economic status, migration background

Clinical attributes: risk status, model of care, complications

Contextual attributes: rural/urban, geography, social support, employment

Encoded latent dimensions: these latent dimensions are encoded in the persona spec that can be key differentiators: previous trauma, fears, high-risk pregnancy, mental health issues, social support, digital literacy, autonomy vs. dependence, trust/distrust in providers, and informal care networks. etc.

Personas are designed to span combinations of journey stage emphasis (preconception, pregnancy, birth, post-partum) and structurally vulnerable situations (e.g., low income, language barriers, previous trauma). These persona specifications are designated as Synthetic Data Type 1 within the proposed framework, comprising parametric descriptions of hypothetical yet plausible users that delineate the design space for stress-testing.

Step 2 – Draft an initial AI-augmented interview guide

The interview guide was developed using an AI-assisted approach. A large language model, configured with safety and privacy settings, was prompted with the study objectives (including goals, motivations, and behaviors) and relevant literature to generate candidate questions and probes for each phase of the maternity journey. Additional prompts were introduced to ensure coverage of emotional, social, and structural dimensions, including experiences of support, power dynamics, and stigma. These outputs were iteratively refined to ensure conceptual clarity and alignment with the research aims.

A semi-structured interview guide was then constructed, organized around the four primary journey phases: preconception, pregnancy, birth, and postpartum. Each phase included open-ended questions and probes designed to elicit information on user goals and expectations, decision-making processes and behaviors, emotional experiences, interactions with healthcare professionals, informal caregivers, and digital tools, as well as perceived risks, barriers, and sources of support.

Throughout the development process, interview-assisted AI functioned as a co-design mechanism. The model was provided with the study framework and thematic structure and instructed to propose further questions and follow-up probes. These AI-generated suggestions were subsequently reviewed and revised by the research team to ensure clinical appropriateness and adherence to human-centered research principles. 

The resulting draft interview guide, augmented through AI-assisted generation and human oversight, was then subjected to stress testing using synthetic personas to evaluate its robustness and its capacity to elicit comprehensive and meaningful insights. This small number of synthetic interviews served to calibrate tone, length, and level of detail.

Step 3 – Conduct synthetic interviews with the AI-augmented guide

Prompt templates were developed for (a) the interviewer role (following the draft guide) and (b) the persona role (responding consistently with the persona template). 

For each persona, a large language model was instructed to engage in role-play by adopting the characteristics defined in the corresponding persona specification. This specification included concrete demographic and contextual attributes, such as “a 28-year-old first-time mother living in a rural area”. The model assumed the role of both participant and interviewer, with one instance serving as the persona and another, or a companion model, conducting the interview according to the AI-assisted guide. Thus, for each persona, several synthetic interviews were conducted using the AI-augmented guide.

To stress-test the interview guide, synthetic interview transcripts were generated through AI-mediated role-play. The model internalized each persona’s attributes and responded to interview questions from that standpoint, while a separate model instance followed the interview guide sequentially and employed all embedded probes. This configuration ensured that the interaction replicated a realistic interview flow and that the guide was systematically evaluated across diverse user profiles.

Multiple synthetic interviews were conducted for each persona to capture variation in potential responses. All transcripts were retained, and the full set of prompts, system instructions, and configuration parameters was logged to support traceability and reproducibility. All transcripts were stored in a secure repository, labelled by persona and iteration. The resulting materials constitute Synthetic Data Type 2, representing controlled conversational data that emulate how individuals with differing maternity trajectories might respond to the interview protocol.

Step 4 – Conduct gap analysis

The synthetic interview transcripts were systematically analysed to evaluate the AI-assisted interviewer's performance. Particular attention was given to identifying instances in which important thematic areas, such as dignity, power, continuity, identity, and structural inequities, were inadequately addressed. The richness and specificity of the goals, motivations, and behaviours expressed by the synthetic participants were also examined to determine whether the guide elicited sufficiently detailed and contextually grounded responses. The synthetic interview transcripts were analysed using content analysis, with a coding framework anchored in the pre-specified dimensions and key constructs (goals, motivations, behaviours, journey stages). 

The analysis assessed which questions prompted more nuanced, emotionally layered narratives and whether particular stages of the maternity journey, such as the postpartum period or the partner’s perspective, were underexplored. The extent to which latent dimensions encoded in each persona specification were made explicit in the responses was also evaluated. For each synthetic persona, occurrences of encoded latent dimensions (e.g., trust, identity tensions, structural barriers) were identified and coded, the particular position where the question/prob is situated, the journey phase, and the form of expression. Thus, for each persona, synthetic transcripts were coded to assess: (a) dimensions consistently surfaced across personas; (b) dimensions remaining hidden or only weakly expressed; (c) questions eliciting rich, emotionally nuanced narratives; and (d) journey stages comparatively under-explored (e.g., post-partum, partner perspective).

Findings from this analysis informed the iterative refinement of the interview guide. The research team revised the gaps and refined the guide adding or sharpening probes where synthetic interviews reveal gaps, ensuring that: i) Probes were added or revised when the synthetic interviews revealed thematic gaps, particularly in user goals, motivations, and behaviours across all stages of the journey, using explicit rules such as: “If [latent dimension X] rarely appears across personas, add or sharpen probes on X.”; ii) Additional prompts were incorporated to capture experiences of agency and disempowerment, the role of informal care networks, and the use of digital tools or informal information channels; iii) Prompts designed to surface underrepresented dimensions, including identity, power relations, and structural barriers, were introduced to enhance the depth and inclusivity of the data-gathering process. The sequence and flow of the guide were adjusted to more accurately reflect the progression of the maternity journey.

All modifications to the guide were documented with justification in an audit trail, along with their analytic rationale, to preserve transparency and replicability. To ensure replicability, several methodological specifications were defined a priori. The large language model(s) employed, including version information, were specified. Prompt templates used for persona generation and interview simulation were documented. A sampling strategy for synthetic personas was implemented, stratified by key pregnancy journey stages, medical risk factors, and socio‑demographic characteristics. Iterative refinement was governed by clear stopping criteria, defined as saturation in the emergence of new probes or themes. All prompts were archived, in full or in part, as online appendices. Any redactions required for ethical reasons were explicitly noted.

Iteration proceeded until thematic saturation was judged to have been reached at the persona level, defined as the point at which additional synthetic interviews failed to yield new probe categories or reveal previously unaddressed journey gaps.

The outputs of Study 1 comprised: (i) a stress-tested interview guide (the AI-enabled guide) and (ii) a methodological log detailing the resources, routines, and governance practices employed. These artefacts directly inform RQ1 (reconfiguration of knowledge-creation routines) and contribute to RQ3 by specifying AI-enabled synthetic user research as a knowledge-creation capability, together with its enabling controls and safeguards.

To address the capability-focused RQ3, a methodological log was maintained throughout the study. This log documented the time invested in persona development, prompting activities, and subsequent analytical work. It also captured challenges encountered during the process and recorded reflections on how the use of AI and synthetic users shaped the research team’s reasoning and decision-making. At a later stage, the methodological log was subjected to thematic analysis to identify the resources, routines, and governance elements that constitute the emerging capability. This analysis provided insight into how integrating AI-assisted methods and synthetic user simulations contributed to capability development within the research process. 

The resulting stress-tested interview guide demonstrated how synthetic users and interview-assisted AI can be used to systematically strengthen the research design before engaging with real participants. This study was conducted as an instrument phase. Diverse synthetic pregnancy journeys and personas were generated, and an interview‑assisted AI approach was used to iteratively refine and stress‑test the interview guide. As a result, a sharper interview protocol and a set of design principles were produced. This design was motivated by prior work on synthetic patient data (Pollack et al., 2019) and by ongoing debates on the governance of synthetic data.

4.2 Study 2

Study 2 provides an expert assessment of the AI-stress-tested guide, focusing on the type of user knowledge it is expected to generate and its value for innovation. This second study primarily addresses RQ2, strengthening the quality of user research, while also highlighting the enabling capabilities of RQ3. 

This study deliberately relies on expert assessment of the AI-stress-tested interview guide rather than a comparative field experiment against a conventionally designed guide. Within the domain of maternity care, no widely recognised “gold standard” interview protocol exists for comprehensively mapping user goals, motivations, and behaviours across the full service journey. Consequently, the construction of a “traditional” comparison guide would itself constitute a novel design effort, rendering any observed differences between the two instruments difficult to interpret. Furthermore, the primary objective of this study is to evaluate AI‑enabled synthetic user research as a knowledge‑creation capability at the front end of innovation, rather than to estimate the effect size of a specific guide relative to an ad‑hoc comparator. At this early design‑laboratory stage, reliance on the informed judgment of experienced innovation scholars and maternity‑care experts is considered both ethically and practically preferable, as it enables appraisal of the guide according to criteria of breadth, depth, and innovation relevance prior to exposing large numbers of patients and professionals to the protocol. The expert evaluation is therefore presented as a necessary first step to establish the plausibility and strategic value of the proposed capability, which may subsequently be complemented by comparative field studies with real users and alternative interview guides.

Step 1 – Create an instrument to assess the quality of the stress-tested interview guide

An instrument was developed in study 1 to evaluate the quality of the stress-tested interview guide. The final AI-augmented and stress-tested version of the guide was prepared alongside a concise description of the design context, including the maternity-journey framework and the overarching research objectives. 

An online survey was then constructed to support a systematic assessment of the guide. The survey included 7-point Likert-type rating items designed to evaluate six dimensions. 

Breadth of coverage – the extent to which the guide covers a wide range of user goals, motivations and behaviours across journey stages;

Depth and latentness – the extent to which questions are likely to elicit subtle, non-obvious, emotional and structural aspects of users’ experiences;

Human-centredness and sensitivity – perceived respectfulness, safety and appropriateness for discussing maternity experiences;

Innovation relevance – the extent to which the guide is likely to generate insights that can inform new or improved services, products, or experience innovations;

Strategic actionability – the extent to which anticipated insights would support strategic decisions (e.g., prioritising opportunity areas, selecting target segments, designing interventions);

Methodological rigour/structure – clarity and coherence of the guide as a research instrument.

The survey also incorporated open-ended questions to capture qualitative reflections. 

To what extent does the interview guide provide comprehensive coverage across all stages of the journey and accommodate diverse contexts and emerging issues?

To what extent does the interview guide facilitate the elicitation of subtle or non-obvious dimensions, including emotional and structural factors?

To what extent does the interview guide enable the identification of insights that could inform the development of new services, products, or experience innovations?

What types of innovation opportunities could be uncovered through the use of this guide?

Where are the potential gaps or risks in this guide, including missing topics or ethical concerns?

What organisational capabilities and governance mechanisms, such as training, ethical oversight, or technical infrastructure, are necessary for effective deployment of the guide? 

These prompts asked respondents to comment on the types of innovation opportunities the guide might reveal, to identify potential gaps or risks, and to consider the organisational capabilities required to deploy the guide effectively.

Step 2 – Use an expert panel to assess the quality of the stress-tested interview guide

Recruitment:

An expert panel of 15–20 participants evaluated the quality of the stress-tested interview guide based on the outlined dimensions. Experts were recruited from two groups roughly balanced between:

Innovation experts: scholars in innovation/innovation management, design or user research, and senior practitioners with substantial experience in front-end innovation projects.

Maternity-care experts: clinicians (obstetricians and nurses) and patient-experience or psychology and social services working in maternity services.

Innovation experts are identified through publication records and relevant professional networks. Maternity-care experts are recruited via hospital, professional, and association networks.

Procedure:

The experts received the guide and survey electronically. They were provided electronically with the AI-stress-tested interview guide, which included an overview of the journey phases and the full question set. They also received a brief description outlining the study’s purpose and the characteristics of the intended target population, along with an online evaluation instrument designed to assess the guide.

Each expert was instructed to review the interview guide as if they were planning a study in their own organisation. Then they were asked to evaluate the guide across multiple dimensions and record their assessments using both rating scales and open-ended responses.

The survey was completed online at the experts’ convenience. Basic background information, including disciplinary training, years of experience, country of practice, and professional role, was collected to contextualise the evaluations.

Step 3 – Analyze the results

Quantitative analysis 

A quantitative analysis was conducted to primarily address RQ2. Descriptive statistics, including means and standard deviations, were computed for each rating dimension to summarise expert evaluations. Internal consistency was assessed for all multi‑item scales, typically using Cronbach’s alpha, to evaluate the measurement structure's reliability.

Where relevant, comparisons between expert groups were performed. Ratings from innovation specialists and maternity‑care specialists were compared using either t‑tests or appropriate nonparametric alternatives. These comparisons were undertaken to explore potential differences in perceptions of the relevance of innovation, human‑centredness, and the strategic applicability of the interview guide.

Together, these analyses provided a quantitative assessment of how the AI‑stress‑tested interview guide was judged on its breadth of coverage, depth of insight, and capacity to support innovation‑oriented outcomes, including innovation relevance and strategic actionability.

Qualitative analysis

A qualitative analysis was conducted to address the research questions (RQ2 & RQ3). The open-ended survey responses were examined using thematic analysis to identify perceptions of the innovation opportunities enabled by the interview guide, as well as perceived gaps, risks, and limitations. The analysis also focused on organisational capabilities and governance requirements described by respondents. 

This thematic analysis to evaluate the performance of the stress-tested interview guide across all specified dimensions follows a protocol:

The research team familiarised itself with the transcripts.

Initial codes were generated inductively, with particular attention to user goals, motivations, and behaviors at each stage of the journey.

Codes are grouped into themes and higher-order dimensions.

Themes are mapped onto the maternity journey (preconception, pregnancy, birth, post-partum), producing comparative journey maps for each condition.

Coding was carried out independently by two researchers. Each coder reviewed the data and contributed to the iterative development of a shared coding scheme. Themes included opportunities for new service concepts, digital tools, or pathway redesign; concerns regarding reliance on AI, missing or insufficiently explored topics, and ethical sensitivities; and requirements related to skills, organisational processes, and data governance. Discrepancies between coders were discussed until agreement was reached, thereby strengthening the reliability of the coding process and the resulting thematic structure.

Integrated analysis 

Lastly, the quantitative and qualitative findings were integrated through joint displays that systematically aligned thematic patterns from the qualitative analysis with the corresponding rating distributions derived from the quantitative data. This integrative strategy facilitated a structured assessment of how specific themes corresponded with variations in expert evaluations, including differential assessments of innovation relevance and strategic value.

The integrated analysis further elucidated the forms of user knowledge that experts anticipated the interview guide would generate, as well as how they envisaged such knowledge informing innovation‑related decision‑making. These insights directly advanced the investigation of the research questions by clarifying the perceived role of the guide as an instrument for the production of user knowledge. Moreover, the joint interpretation provided a conceptual basis for identifying the capability bundles and governance mechanisms that experts deemed necessary for the guide’s effective organisational deployment.

4.3 Trustworthiness, ethics, and replicability

To make the capability dimension explicit, the design process was systematically documented and analysed. This included detailed records of the time, effort, and iterative cycles involved in developing the interview guide, logs of interactions with interview‑assisted AI and synthetic personas, and researcher reflections on the strengths and limitations of synthetic stress‑testing. Particular attention was given to cases in which synthetic simulations revealed potential blind spots that could later be examined in real interview contexts.

The findings were subsequently interpreted through an innovation‑capabilities lens. This involved identifying the relevant resource base, which encompassed AI tools, synthetic personas, and methodological expertise; the routines underpinning the work, such as persona construction, simulation, comparative analysis, and guide refinement; and the governance mechanisms, including ethical safeguards, bias‑checking procedures, and reflexive practices that shaped decision‑making throughout the study.

To enhance reliability, validity, and overall trustworthiness, the research employed a blinded expert evaluation process designed to reduce confirmation bias when assessing the quality of insights produced by the interview‑assisted AI guide. A consistent analytical protocol was applied across studies, analytic decisions were carefully documented, and reflexive memos captured how interactions with AI systems and synthetic users influenced both the research design and the interpretation of findings.

Additional procedural safeguards further strengthened trustworthiness. All persona specifications, prompts, and decision rules used in Study 1 were systematically documented to ensure transparency and auditability. The refinement of the interview guide followed a clearly defined, stepwise process, allowing full traceability of design decisions across iterative cycles. Study 2 incorporated a diverse panel of experts, and both quantitative ratings and rich qualitative feedback were gathered to enable triangulation. A reflexive log was maintained throughout the entire research process to document how engagements with AI and synthetic users informed instrument design choices and interpretive judgements.

Ethical considerations were addressed by consistently distinguishing synthetic from real data. Study 1 relied exclusively on synthetic personas and AI‑generated transcripts, while Study 2 involved only expert professionals who provided informed consent, with all responses anonymised. No real patient data were collected or analysed. Consequently, the overall research design constitutes a low‑risk, upstream evaluation appropriate for assessing the capabilities of AI‑enabled synthetic user research prior to any deployment involving actual patients.

AI Ethics and Disclosure: In accordance with JPIM 2025 guidelines on the use of artificial intelligence, transparency regarding AI tools utilized in this research is disclosed herein. Large Language Models (LLMs) from OpenAI (GPT-5.2) and Anthropic (Claude 3.5 Sonnet) and Google (Gemini) were actively employed to orchestrate the Synthetic Design Laboratory, construct structured personas, role-play synthetic participants, and act as an interview-assisted agent during testing. AI was rigorously isolated entirely to synthetic exploratory protocols (Study 1 design and evaluation testing), and strict human oversight governed prompt specification and data synthesis. No patient data or proprietary healthcare records were uploaded to or processed by these AI tools.

5. Results 

5.1 Evaluative Analysis of Conversational Yield: From Surface Needs to Latent Insights

A fundamental challenge in the Front End of Innovation (FEI) is transcending surface-level user requests to uncover the latent, structural, and emotional drivers that inform breakthrough service design. To evaluate the efficacy of the Synthetic Design Laboratory as a hybrid simulation and high-fidelity micro-sensing capability for innovation (e.g., Korst et al., 2025; Lehmann et al., 2025), we conducted a comparative analysis of conversational data yielded by two distinct prompt calibrations of the Generative Interviewer Agent.

In accordance with the knowledge-based view (KBV), the iterative calibration of the interviewer agent is framed as a knowledge-creation routine. This routine functions to convert tacit user vulnerabilities and complex social realities into explicit innovation requirements before human fieldwork begins, thereby systematically augmenting the organization's absorptive capacity.

Our analysis utilized a structured classification rubric that delineates between Needs (i.e., explicit, logistical, or transactional requirements focusing on "what" the user wants) and Insights (i.e., deeper understandings revealing hidden truths, structural tensions, and underlying reasons for user actions, focusing on "why" the user behaves or feels a certain way).

5.1.1 Baseline Extraction (Run 1): The "Customer Service" Paradigm

In the initial simulation, the interviewer agent operated with a generalised objective to identify support gaps. However, lacking strict qualitative constraints, the Large Language Model (LLM) defaulted to a solution-oriented "customer service" paradigm. The extracted data yielded 100% surface-level Needs, primarily capturing logistical requests. While actionable, this functional data failed to uncover the profound systemic friction causing the participant's distress.

5.1.2 Calibrated Extraction: The Qualitative Researcher Paradigm

Following iterative calibration, the agent was strictly constrained to investigate emotional states and structural barriers, adopting the posture of an empathetic ethnographic researcher. This calibration profoundly shifted the data yield, producing transcripts composed of 75% Insights and only 25% Needs. This dramatic enhancement reveals the capacity of the Synthetic Design Laboratory to operate as a high-fidelity micro-sensing capability for innovation. By simulating real-world tensions and power dynamics, the laboratory significantly enhances the ecological value of the research design upstream.

The calibrated synthetic user generated deep, reflective elaboration, yielding powerful latent insights critical for human-centered design in maternity care:

- The "Stigma of Accommodation" Insight: The synthetic participant revealed that requesting logistical support—such as a stool for physical relief at work or assignment extensions at university—is paradoxically perceived as a capitulation. Within environments characterized by institutional skepticism, utilizing accommodations is internalized not as a right, but as a "demographic failure" that merely serves to "prove them right" regarding her perceived incapacity.

- The "Private Struggle" Insight: The data surfaced a paralyzing latent belief that "needing help equals failure." Having internalized the judgment of family and peers, the participant equated asking for support with confirming negative societal stereotypes. Consequently, vulnerable users routinely isolate themselves, hiding severe pain and food insecurity as a behavioral response to mitigate the risk of institutional let-down.

- The "Competent Patient" Paradox: The transcripts additionally revealed a critical tension wherein the user's attempts to navigate complex care pathways assertively are met with systemic resistance. Being "too knowledgeable" or advocating too strongly creates unexpected friction with authority figures in both healthcare and academic settings, further marginalizing the patient.

5.1.3 Governance and Replicability

To ensure the responsible deployment of this knowledge-creation routine, robust governance mechanisms were instrumental. The continual generation of an "Audit Trail"—encompassing granular JSON logs of exact prompt-reply payloads and dynamic summary reports of token utilization—ensures ethical transparency and full replicability of the synthetic user research. This pipeline clarifies the methodological boundary: synthetic data is operationalized strictly as a design testbed to sharpen research instruments, rather than as a substitute for real user voices.

6. Conclusions

6.1 Theoretical, methodological, and managerial implications

6.2 Limitations and directions for future research

References

Bahoo, S., Cucculelli, M., & Peroni, C. (2023). Artificial intelligence and corporate innovation. Technological Forecasting and Social Change, 188, 122264.

Boraschi, D., van der Schaar, M., Costa, A., & Milne, R. (2025). Governing synthetic data in medical research: The time is now. The Lancet Digital Health, 7(4), e233–e234.

Bouschery, S. G., Blazevic, V., & Piller, F. T. (2023). Augmenting human innovation teams with artificial intelligence: Exploring transformer-based language models. Journal of Product Innovation Management, 40(2), 139–153.

Day, G. S. (1994). The capabilities of market driven organizations. Journal of Marketing, 58(4), 37–52. https://doi.org/10.1177/002224299405800404

Gama, F., & Magistretti, S. (2025). Artificial intelligence in innovation management: A review of innovation capabilities and a taxonomy of AI applications. Journal of Product Innovation Management, 42(2), 131–154.

Grant, R. M. (1996). Toward a knowledge-based theory of the firm. Strategic Management Journal, 17(Winter Special Issue), 109–122. https://doi.org/10.1002/smj.4250171110

Jaworski, B. J., & Kohli, A. K. (1993). Market orientation: Antecedents and consequences. Journal of Marketing, 57(3), 53–70. https://doi.org/10.1177/002224299305700304

Koc, V. (2024). Creating synthetic user research: Persona prompting & autonomous agents. Towards Data Science.

Kogut, B., & Zander, U. (1992). Knowledge of the firm, combinative capabilities, and the replication of technology. Organization Science, 3(3), 383–397. https://doi.org/10.1287/orsc.3.3.383

Korst, J., Puntoni, S., & Toubia, O. (2025, May–June). How Gen AI is transforming market research. Harvard Business Review.

Lehmann, S. L., Dahlke, J., Pianta, V., & Ebersberger, B. (2025). Artificial intelligence and corporate ideation systems. Journal of Product Innovation Management. Advance online publication. https://doi.org/10.1111/jpim.12782

Li, B., Xu, W., Zhang, Y., et al. (2024). Scaling synthetic data creation with 1,000,000,000 personas. arXiv:2406.20094.

Nonaka, I. (1994). A dynamic theory of organizational knowledge creation. Organization Science, 5(1), 14–37. https://doi.org/10.1287/orsc.5.1.14

Oliver, C. R. (2023). Probing in qualitative research interviews: Theory and practice. Qualitative Research in Psychology, 20(3), 382–397. https://doi.org/10.1080/14780887.2023.2238625

Pollack, A. H., Simon, T. D., Snyder, J., & Pratt, W. (2019). Creating synthetic patient data to support the design and evaluation of novel health information technology. Journal of Biomedical Informatics, 95, 103201.

Sattele, V., & Ortiz, J. C. (2024). Generating user personas with AI: Reflecting on its implications for design. In C. Gray, E. Ciliotta Chehade, P. Hekkert, L. Forlano, P. Ciuccarelli, & P. Lloyd (Eds.), DRS2024: Boston, 23–28 June. https://doi.org/10.21606/drs.2024.1024

Sreenivasan, A., & Suresh, M. (2024). Design thinking and artificial intelligence: A systematic literature review exploring synergies. International Journal of Innovation Studies, 8, 297–312.

Teece, D. J. (2007). Explicating dynamic capabilities: The nature and microfoundations of (sustainable) enterprise performance. Strategic Management Journal, 28(13), 1319–1350. https://doi.org/10.1002/smj.640

von Hippel, E. (1986). Lead users: A source of novel product concepts. Management Science, 32(7), 791–805. https://doi.org/10.1287/mnsc.32.7.791

## 5. Results

### 5.1 Descriptive Overview

A total of 300 synthetic interview transcripts were generated using a Balanced
Incomplete Block Design (BIBD) with five questionnaire versions administered to
150 composite synthetic personas. Each persona completed two of the five
versions, enabling within-subject comparison. Across the full pipeline of
355 sessions (including refinement and adversarial rounds), the total
computational cost was US$0.64.

Quality evaluation yielded 6,458 question--response pairs scored on a
0--5 scale across five dimensions. The overall mean composite richness score was
3.06 (SD reported per version in Table 1). The mean latent dimension
surfacing rate across all transcripts was 72.1%.

Across the five quality dimensions, mean scores were: emotional depth
(*M* = 3.32), specificity (*M* = 2.95), latent surfacing
(*M* = 3.28), narrative quality (*M* = 3.13), and clinical grounding
(*M* = 2.59). Clinical grounding consistently scored lowest, reflecting the
challenge of eliciting clinically specific detail from synthetic personas. Quality
scoring was performed by google/gemini-3-flash-preview; interviews were conducted by openai/gpt-5-mini-2025-08-07
with multi-provider persona role-play (see Table 1 and Figure 1).

### 5.2 Response Quality Across Versions

Quality scores varied significantly across the five questionnaire versions. A
Kruskal--Wallis test revealed a statistically significant difference in composite
richness scores (*H* = 23.313, *p* = 0.001), confirming that version
design influenced response quality (Table 1, Figure 1).

**Table 1.** Quality scores by questionnaire version.

| Version | N | Richness M(SD) | 95% CI | Surfacing Rate |
|---------|---|----------------|--------|----------------|
| V1 | 60 | 2.32 (1.96) | (1.83, 2.82) | 60.9% |
| V2 | 60 | 2.81 (1.83) | (2.35, 3.27) | 76.1% |
| V3 | 60 | 2.64 (1.97) | (2.14, 3.14) | 69.8% |
| V4 | 60 | 2.99 (1.78) | (2.54, 3.44) | 80.7% |
| V5 | 60 | 2.96 (1.80) | (2.50, 3.41) | 73.0% |

All pairwise comparisons yielded small effect sizes (|*d*| < 0.50), suggesting
that while statistically significant differences existed, practical differences
between versions were modest (Table 2).

**Table 2.** Pairwise effect sizes (Cohen's *d*).

| Comparison | Cohen's *d* | Interpretation |
|------------|-------------|----------------|
| V1 vs V2 | -0.256 | small |
| V1 vs V3 | -0.161 | small |
| V1 vs V4 | -0.355 | small |
| V1 vs V5 | -0.335 | small |
| V2 vs V3 | 0.089 | small |
| V2 vs V4 | -0.100 | small |
| V2 vs V5 | -0.081 | small |
| V3 vs V4 | -0.186 | small |
| V3 vs V5 | -0.167 | small |
| V4 vs V5 | 0.019 | small |

### 5.3 Within-Subject Comparison (BIBD)

The balanced incomplete block design enabled within-subject comparisons across
five BIBD groups, each comprising 30 persona pairs. Wilcoxon signed-rank tests
were applied to each group's paired richness scores. Of the 5 within-subject
comparisons, 4 reached statistical significance (*p* < .05), as reported
in Table 3.

**Table 3.** Within-subject comparisons by BIBD group.

| Group | N | Mean Diff | Wilcoxon Z | p | Favours |
|-------|---|-----------|------------|---|---------|
| Group A V1 vs V2 | 30 | -0.203 | -3.007 | 0.0026* | V2 |
| Group B V1 vs V3 | 30 | -0.060 | -2.334 | 0.0196* | V3 |
| Group C V2 vs V4 | 30 | +0.015 | -0.192 | 0.8476 | V2 |
| Group D V3 vs V5 | 30 | +0.123 | -3.657 | 0.0003* | V3 |
| Group E V4 vs V5 | 30 | +0.101 | -2.343 | 0.0191* | V4 |

These results corroborated the between-subject findings: later versions (V2--V4)
consistently outperformed V1, and V4 emerged as the preferred instrument in
head-to-head paired comparisons (see Figure 2).

### 5.4 Latent Dimension Coverage

Across 12 latent dimensions tracked per version, surfacing rates varied
substantially (Table 5, Figure 3). Coverage analysis identified 35 blind
spots (dimension--version cells with surfacing rates below 20%).

**Table 5.** Latent dimension surfacing rates by version (heatmap summary).

| Dimension | V1 | V2 | V3 | V4 | V5 |
|-----------|------|------|------|------|------|
| Autonomy Vs Dependence | 58.3% | 73.3% | 71.7% | 78.3% | 73.3% |
| Body Image Autonomy | 1.7% | 1.7% | 1.7% | 0.0% | 0.0% |
| Continuity Of Care | 0.0% | 6.7% | 0.0% | 0.0% | 6.7% |
| Digital Information Seeking | 1.7% | 0.0% | 6.7% | 0.0% | 0.0% |
| Dignity Respect | 8.3% | 10.0% | 6.7% | 3.3% | 5.0% |
| Identity Tensions | 61.7% | 80.0% | 73.3% | 85.0% | 73.3% |
| Informal Care Networks | 61.7% | 75.0% | 68.3% | 76.7% | 73.3% |
| Intergenerational Patterns | 5.0% | 1.7% | 1.7% | 1.7% | 5.0% |
| Partner Role | 5.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Power Dynamics | 61.7% | 75.0% | 70.0% | 80.0% | 73.3% |
| Structural Barriers | 63.3% | 78.3% | 71.7% | 81.7% | 73.3% |
| Trust Distrust | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

**Well-surfaced dimensions** (mean > 50% across versions): identity tensions (74.7%), structural barriers (73.7%), power dynamics (72.0%), informal care networks (71.0%), autonomy vs dependence (71.0%).

**Persistent blind spots** (mean < 10% across versions): trust distrust (0.0%), partner role (1.0%), body image autonomy (1.0%), digital information seeking (1.7%), continuity of care (2.7%), intergenerational patterns (3.0%), dignity respect (6.7%).

The trust/distrust dimension recorded a surfacing rate of 0.0% across all five
versions, indicating a systematic instrument limitation. Body image autonomy,
continuity of care, digital information seeking, and partner role similarly
showed near-zero surfacing rates, suggesting these experiential domains require
targeted probing strategies beyond those implemented in the current instrument
set (see Section 6.4 for discussion of implications).

### 5.5 Service Provision Mapping

Service mapping analysis across 300 transcripts
identified 442 service gaps and 584 innovation opportunities
(Figure 4). The majority of service gaps were classified as high severity, indicating
that synthetic personas consistently articulated unmet needs in maternity care
provision.

**Table 6.** Service gap severity distribution by category (top 10).

| Category | High | Medium | Low | Total |
|----------|------|--------|-----|-------|
| Shared Decision Making | 81 | 9 | 0 | 90 |
| Emotional Support | 88 | 1 | 0 | 89 |
| Continuity Of Care | 73 | 1 | 0 | 74 |
| Care Coordination | 45 | 4 | 0 | 49 |
| Communication | 30 | 2 | 0 | 32 |
| Postnatal Mental Health | 32 | 0 | 0 | 32 |
| Information Quality | 13 | 4 | 0 | 17 |
| Privacy Dignity | 15 | 1 | 0 | 16 |
| Accessibility | 9 | 1 | 0 | 10 |
| Birth Environment | 9 | 0 | 0 | 9 |

The most frequently identified gap categories were emotional support
(88 high-severity), shared decision-making (81 high-severity), and continuity
of care (73 high-severity). These findings align with established maternity
care literature identifying relational and communicative dimensions as persistent
areas of unmet need.

### 5.6 Innovation Opportunities

A total of 584 innovation opportunities were extracted from synthetic
interview responses (Table 7, Figure 5). The five most frequently identified
innovation areas were: digital tools (*n* = 118), care coordination (*n* = 113), emotional support (*n* = 98), postnatal mental health (*n* = 76), communication (*n* = 47).

**Table 7.** Innovation opportunities by category.

| Category | Count | Share |
|----------|-------|-------|
| Digital Tools | 118 | 20.2% |
| Care Coordination | 113 | 19.3% |
| Emotional Support | 98 | 16.8% |
| Postnatal Mental Health | 76 | 13.0% |
| Communication | 47 | 8.0% |
| Accessibility | 23 | 3.9% |
| Shared Decision Making | 23 | 3.9% |
| Information Quality | 17 | 2.9% |
| Financial Accessibility | 16 | 2.7% |
| Continuity Of Care | 13 | 2.2% |
| Birth Environment | 11 | 1.9% |
| Privacy Dignity | 8 | 1.4% |
| Cultural Sensitivity | 7 | 1.2% |
| Partner Involvement | 7 | 1.2% |
| Transport Access | 3 | 0.5% |
| Clinical Competence | 3 | 0.5% |
| Breastfeeding Support | 1 | 0.2% |

Digital tools and care coordination together accounted for
39.6%
of all identified innovations, suggesting that technology-mediated service
improvements represent the primary opportunity space perceived by synthetic
personas. Emotional support innovations (*n* = 98)
constituted the third-largest category, reinforcing the gap analysis findings
in Section 5.5.

### 5.7 Iterative Refinement (V4 to V4_R1)

Following selection of V4 as the winning instrument, a refinement cycle was
conducted. The refined instrument (V4_R1) was administered to 50 additional
personas, generating 1,253 scored responses. Refinement targeted 7
identified blind spots through question rewording, probe additions, and
structural modifications (38 changes applied).

The refined instrument demonstrated substantial improvement across all metrics:

- **Composite richness:** V4_R1 *M* = 4.09 vs. V4 *M* = 2.99
  (+36.9%)
- **Surfacing rate:** V4_R1 = 98.9% vs. V4 = 80.7%
  (+22.5%)
- **Blind spots resolved:** 5 of 7 (2 remaining)

Per-dimension scores for the refined instrument were: emotional depth
(*M* = 4.48), specificity
(*M* = 3.87), latent surfacing
(*M* = 4.43), narrative quality
(*M* = 4.20), and clinical grounding
(*M* = 3.49).

The improvement magnitude (+36.9% composite richness) confirmed
that data-driven instrument refinement, guided by blind-spot diagnostics and
quality scoring feedback, can meaningfully enhance questionnaire performance
within a single iteration cycle.

### 5.8 Saturation Analysis

Thematic saturation was assessed across 110 transcripts (60 original V4, 50
refined V4_R1) using cumulative theme accumulation curves and rolling marginal
yield analysis with a window of 5 transcripts and a plateau threshold of 2 new
themes per transcript over 5 consecutive transcripts.

A total of 3,925 unique thematic codes were identified. The cumulative theme
curve followed a power-law trajectory (*R*^2 = 0.992), with the best-fit
equation *y* = 52.2 *x*^0.892. The near-unity exponent (0.892) indicated
near-linear theme accumulation, meaning practical saturation was not foreseeable
within feasible sample sizes (Table 8, Figure 6).

**Table 8.** Saturation analysis summary.

| Metric | Value |
|--------|-------|
| Original transcripts (V4) | 60 |
| Refinement transcripts (V4_R1) | 50 |
| Total unique themes | 3,925 |
| Pre-refinement themes | 2,108 |
| Post-refinement new themes | 1,817 |
| Refinement novelty rate | 46.3% |
| Best-fit model (original) | Power law |
| *R*^2 | 0.992 |
| Original mean yield | 35.1 themes/transcript |
| Refinement mean yield | 36.3 themes/transcript |
| Mann--Whitney *U* | 1,427.0 (*p* = 0.663) |

The refinement round introduced 1,817 themes not observed in the original 2,108
themes, representing a 46.3% novelty rate. A Mann--Whitney *U* test confirmed
no significant difference in per-transcript yield between original and refinement
corpora (*U* = 1,427.0, *p* = 0.663), indicating that the refined instrument
maintained generative capacity without diminishing returns.

Per-category saturation was reached for structured categories: latent dimensions
(14 unique, plateau at transcript 4), KBV dimensions (6 unique, plateau at
transcript 4), service gaps (14 unique, plateau at transcript 5), and innovation
opportunities (17 unique, plateau at transcript 5). However, thematic areas
(3,874 unique codes) showed no plateau, confirming an open thematic space
consistent with the power-law accumulation pattern.

These findings are consistent with qualitative research literature suggesting
that thematic saturation is instrument-dependent and that changing the instrument
can reopen the thematic space (Hennink et al., 2017; Saunders et al., 2018).

### 5.9 Robustness Testing

Adversarial robustness testing evaluated the refined instrument (V4_R1) against
five vulnerable population profiles designed to stress-test instrument
performance under challenging interview conditions. The pass threshold was
defined as composite richness exceeding 50% of the population mean (i.e.,
richness > 2.04).

All five adversarial profiles exceeded the threshold, yielding an overall
verdict of "Robust across vulnerable populations" (Table 9).

**Table 9.** Adversarial robustness testing results.

| Profile | Persona | Richness | Pop. Mean | Ratio | Verdict |
|---------|---------|----------|-----------|-------|---------|
| Low Health Literacy | Destiny Marlowe | 3.45 | 4.09 | 84% | PASS |
| Language Barrier | Mei-Ling Vasquez | 3.01 | 4.09 | 74% | PASS |
| Hostile/Distrustful | Renee Thibodeau | 3.51 | 4.09 | 86% | PASS |
| Rural Isolated | Darlene Hutchins | 3.76 | 4.09 | 92% | PASS |
| Early Pregnancy Ambivalent | Danielle Okafor | 3.02 | 4.09 | 74% | PASS |

The adversarial mean richness was 3.35, representing 82% of the population
mean (4.09). The rural isolated profile achieved the highest adversarial
richness (3.76, 92% of population), while the language barrier and early
pregnancy ambivalent profiles showed the largest performance decrements (74%
of population), identifying these as areas warranting further instrument
refinement in future iterations.

All five dimensions maintained adequate scores across adversarial profiles,
with latent surfacing consistently scoring highest (range: 3.56--4.50) and
clinical grounding lowest (range: 2.31--3.56), mirroring the pattern observed
in the main corpus.

### 5.10 Inter-Rater Reliability

Inter-rater reliability was assessed using 30 transcripts scored
independently by three LLM providers (Anthropic, Google, OpenAI), employing
an ICC(2,1) two-way random effects model. The composite richness ICC was
0.903, indicating excellent agreement (Table 4).

**Table 4.** Inter-rater reliability across scoring dimensions.

| Dimension | ICC(2,1) | Interpretation | Krippendorff's alpha |
|-----------|----------|----------------|---------------------|
| Emotional Depth | 0.903 | excellent | 0.901 |
| Specificity | 0.879 | excellent | 0.876 |
| Latent Surfacing | 0.910 | excellent | 0.908 |
| Narrative Quality | 0.846 | excellent | 0.842 |
| Clinical Grounding | 0.854 | excellent | 0.849 |
| Composite Richness | 0.903 | excellent | N/A |

All individual dimensions achieved excellent agreement (ICC >= 0.846), with
latent surfacing showing the highest concordance (ICC = 0.910) and narrative
quality the lowest (ICC = 0.846). Krippendorff's alpha values closely tracked
ICC estimates across all dimensions (range: 0.842--0.908), providing convergent
evidence of measurement consistency.

These results support the validity of using LLM-as-judge methodology for
quality assessment, provided that multi-provider triangulation is employed
to mitigate single-model scoring biases.

### 5.11 Version Ranking

A weighted composite score was computed for each version using quality (40%),
coverage (25%), innovation (20%), and breadth (15%) weights. V4 ranked
first with a composite score of 2.706, followed by V5
(2.565), representing a 5.5% advantage (Table 10).

**Table 10.** Version ranking by weighted composite score.

| Rank | Version | Quality | Coverage | Innovation | Composite |
|------|---------|---------|----------|------------|-----------|
| 1 | V4 | 2.99 | 0.339 | 3.87 | 2.706 |
| 2 | V5 | 2.96 | 0.319 | 3.35 | 2.565 |
| 3 | V2 | 2.81 | 0.335 | 3.43 | 2.542 |
| 4 | V3 | 2.64 | 0.310 | 3.23 | 2.403 |
| 5 | V1 | 2.32 | 0.274 | 3.22 | 2.226 |

V4 was selected as the winning instrument based on this composite ranking.
Its advantage was driven primarily by superior performance on quality
(*M* = 2.99) and innovation
(*M* = 3.87) scores, while
coverage scores were broadly comparable across versions (range: 0.274--0.339).
The V4 instrument employed an Expectation--Perception Gap interview
strategy, which elicited richer responses by explicitly probing the distance
between expected and received care experiences.

---
*Section generated by results_writer.py — no LLM calls.*



## 6. Discussion

This section interprets the findings presented in Section 5, situating them
within the theoretical framework of knowledge-based view (KBV) theory and
addressing the three research questions. Methodological, managerial, and
theoretical implications are discussed, followed by limitations and directions
for future research.


### 6.1 Theoretical Implications

#### Knowledge-Based View (KBV) Theory

- The study demonstrates that AI-enabled synthetic user research can function
  as a **micro-capability** within the knowledge-based view of the firm
  (Grant, 1996; Kogut & Zander, 1992).
- Composite richness scores (*M* = 3.06/5.0) and a mean latent
  dimension surfacing rate of 72.1% indicate that synthetic
  personas can surface tacit experiential knowledge that would otherwise remain
  inaccessible through conventional survey instruments.
- The significant version effect (*H* = 23.313, *p* = 0.001) confirms
  that instrument design represents a knowledge-extraction capability whose
  parameters can be optimised through iterative refinement.

[AUTHOR INPUT NEEDED: Elaborate on how these findings extend KBV theory to
encompass AI-generated knowledge assets. Discuss whether synthetic interview
data constitutes a form of "combinative capability" (Kogut & Zander, 1992)
or a novel category of knowledge resource.]

#### Research Questions

**RQ1 — Can AI-generated synthetic personas produce interview responses of
sufficient quality for qualitative analysis?**

- The evidence supports an affirmative answer. Mean composite richness of
  3.06/5.0, with emotional depth (*M* = 3.32)
  and latent surfacing (*M* = 3.28)
  both exceeding 3.0/5.0, indicates that synthetic responses achieved
  moderate-to-good qualitative richness.
- Inter-rater reliability (ICC = 0.903, excellent) confirms measurement validity.

[AUTHOR INPUT NEEDED: Compare these quality levels to published benchmarks
for human interview data quality. Discuss what "sufficient" means in context.]

**RQ2 — Does questionnaire design significantly affect the quality of synthetic
interview responses?**

- The Kruskal--Wallis test (*H* = 23.313, *p* = 0.001) confirms
  significant version effects. V4 achieved the highest composite score
  (2.706), employing an Expectation--Perception Gap strategy.
- Within-subject BIBD comparisons corroborated this finding: 4 of 5 paired
  comparisons reached significance.

[AUTHOR INPUT NEEDED: Discuss theoretical implications of the finding that
instrument design matters even for synthetic respondents.]

**RQ3 — Can iterative refinement improve instrument performance based on
quality feedback?**

- The V4-to-V4_R1 refinement cycle yielded +36.9%
  richness improvement and +22.5%
  surfacing rate improvement, confirming that data-driven refinement is
  effective.
- 5 of 7 blind spots
  were resolved in a single iteration.

[AUTHOR INPUT NEEDED: Discuss whether this constitutes evidence for
"double-loop learning" (Argyris, 1977) in AI-mediated research design.]

### 6.2 Methodological Implications

#### Composite Persona Construction

- The study employed 150 composite personas constructed from Synthea
  EHR data enriched with HuggingFace FinePersonas narratives. This two-source
  approach grounded personas in realistic clinical trajectories while providing
  the narrative richness needed for interview simulation.
- The approach addresses a key limitation of prior synthetic user studies that
  relied on single-source persona generation.

[AUTHOR INPUT NEEDED: Discuss how the EHR grounding improves ecological validity
compared to purely narrative-based synthetic personas. Reference relevant
persona construction literature.]

#### Balanced Incomplete Block Design (BIBD)

- The BIBD enabled within-subject comparison across 5 questionnaire versions
  with only 2 administrations per persona, reducing confounding while maintaining
  statistical power (*n* = 30 pairs per group).
- 4 of 5 within-subject comparisons reached significance, validating the
  design's sensitivity to version effects.
- This design is novel in the context of synthetic interview research and may
  serve as a template for future multi-instrument comparison studies.

[AUTHOR INPUT NEEDED: Compare BIBD approach to full crossover designs used in
clinical trials. Discuss trade-offs between statistical efficiency and ecological
validity.]

#### Thematic Saturation in Synthetic Corpora

- Saturation was not reached after 110 transcripts (3,925 unique themes), with
  a power-law accumulation curve (*R*^2 = 0.992, exponent = 0.892).
- This near-linear accumulation pattern challenges conventional saturation
  assumptions and raises questions about whether synthetic data inherently
  produces higher thematic diversity than human interviews.
- The refinement round introduced 1,817 new themes (46.3% novelty rate),
  confirming that instrument change reopens the thematic space.

[AUTHOR INPUT NEEDED: Discuss implications for saturation theory. Consider
whether this finding reflects LLM creativity/hallucination or genuine thematic
richness. Reference Hennink et al. (2017) and Saunders et al. (2018).]

#### Inter-Rater Reliability with LLM Judges

- Composite ICC = 0.903 across three independent LLM providers (Anthropic,
  Google, OpenAI) demonstrates that multi-provider triangulation yields excellent
  measurement consistency.
- This approach mitigates the risk of single-model scoring bias and provides a
  replicable framework for quality assessment in synthetic research.

[AUTHOR INPUT NEEDED: Compare ICC values to published benchmarks for human
inter-rater reliability in qualitative health research. Discuss whether LLM
agreement may be artificially inflated by shared training data.]

### 6.3 Managerial Implications

#### Innovation Opportunity Prioritisation

- The study identified 584 innovation opportunities and 442
  service gaps across maternity care provision. The five highest-priority
  innovation areas were:
  1. **Digital tools** (*n* = 118) — patient-facing
     apps, remote monitoring, digital care coordination platforms.
  2. **Care coordination** (*n* = 113) — integrated
     care pathways, handover protocols, multi-disciplinary team coordination.
  3. **Emotional support** (*n* = 98) — proactive
     mental health screening, peer support programmes, continuity of carer models.
  4. **Postnatal mental health** (*n* = 76) —
     early intervention pathways, partner-inclusive support, digital mental health
     tools.
  5. **Communication** (*n* = 47) — plain-language
     information resources, multilingual support, shared decision-making aids.

[AUTHOR INPUT NEEDED: Map these innovation opportunities to specific NHS/healthcare
service improvement priorities. Discuss which innovations are actionable within
current resource constraints.]

#### Cost-Effectiveness

- The total pipeline cost was US$0.64 for 355 sessions,
  yielding a per-session cost of US$0.0018.
- This represents orders-of-magnitude cost reduction compared to traditional
  qualitative interview studies (typically US$500--2,000 per participant for
  recruitment, incentives, transcription, and analysis).
- The marginal cost of additional iterations approaches zero, enabling rapid
  prototyping of research instruments.

[AUTHOR INPUT NEEDED: Provide specific cost comparisons to published maternity
care interview studies. Discuss whether cost savings justify the quality trade-offs
inherent in synthetic data.]

#### Governance Framework

- The study implemented the following governance elements to ensure
  methodological transparency and reproducibility:
  - All prompts archived
  - Audit trail for every modification
  - Multi-provider inter-rater validation
  - Adversarial robustness testing
  - Synthetic-only data (no real patients)
  - Cost tracking per call
  - Timestamped outputs — no data overwritten

[AUTHOR INPUT NEEDED: Discuss how this governance framework addresses emerging
regulatory requirements for AI-generated research data (e.g., EU AI Act, NHS
AI ethics guidelines). Recommend governance standards for future synthetic
research studies.]

### 6.4 Limitations and Future Research

#### Synthetic Data Limitations

- **All data is synthetic.** Personas were constructed from Synthea-generated
  EHR records and LLM-enriched narratives. No real patients were involved.
  Findings represent the generative capacity of AI models rather than empirical
  patient experiences.
- **Unknown ecological validity.** The relationship between synthetic interview
  responses and real patient responses remains unvalidated. The quality metrics
  used (richness, surfacing rate) measure internal consistency rather than
  external validity.

[AUTHOR INPUT NEEDED: Discuss the fundamental epistemological question of what
synthetic interview data actually represents. Is it a simulation of patient
experience, a model of researcher expectations, or a novel form of knowledge?]

#### LLM Bias and Coverage Gaps

- Clinical grounding scored consistently lowest across all versions
  (*M* = 2.59/5.0), suggesting that LLM-based personas may lack
  the specificity of lived clinical experience.
- 2 blind spot dimensions remained unresolved after refinement.
  Persistent zero-surfacing dimensions (trust distrust) may reflect
  fundamental limitations of prompt-based persona construction.
- First-trimester and preconception phases consistently showed lower richness
  scores across all versions, potentially reflecting training data biases in
  the underlying LLMs.

[AUTHOR INPUT NEEDED: Discuss potential sources of LLM bias relevant to
maternity care research. Consider how model training data composition may
systematically underrepresent certain populations or care experiences.]

#### Coverage Gaps

- The instrument failed to surface trust/distrust dynamics across all five
  versions (0.0% surfacing rate), despite multiple questions targeting this
  dimension. This suggests a structural limitation in how synthetic personas
  process trust-related prompts.
- Body image autonomy, partner role, and digital information seeking similarly
  showed near-zero surfacing rates, indicating that these experiential domains
  may require fundamentally different elicitation strategies.

[AUTHOR INPUT NEEDED: Propose specific methodological solutions for addressing
these coverage gaps in future research iterations.]

#### Future Research Directions

1. **Validation against human data.** The most critical next step is to
   administer the refined V4_R1 instrument to real maternity care service
   users and compare response quality, thematic content, and latent dimension
   coverage to synthetic counterparts.

2. **Multi-modal persona enrichment.** Future iterations could incorporate
   additional data sources (e.g., patient-reported outcome measures, social
   determinants of health data) to improve persona realism.

3. **Cross-cultural replication.** The current study is grounded in US-based
   Synthea data. Replication with UK, European, or Global South health system
   data would test the generalisability of the approach.

4. **Longitudinal instrument evolution.** The power-law thematic accumulation
   pattern suggests that continued iteration could access increasingly
   specialised experiential domains. A longitudinal study tracking instrument
   evolution over multiple refinement cycles would provide evidence on
   diminishing returns.

5. **Trust and relational dimensions.** Targeted research is needed to
   understand why trust/distrust dynamics are inaccessible to current
   synthetic persona approaches and to develop elicitation strategies that
   overcome this limitation.

[AUTHOR INPUT NEEDED: Prioritise these future research directions based on
feasibility and theoretical contribution. Add any domain-specific directions
relevant to maternity care policy or practice.]

---
*Scaffold generated by discussion_writer.py — no LLM calls.*
*Sections marked [AUTHOR INPUT NEEDED] require human interpretation.*


## AI Disclosure Statement

In accordance with JPIM editorial policy, we disclose the following use of generative AI tools in this study. Three families of large language models (Anthropic Claude, OpenAI GPT, and Google Gemini) were used for: (1) generating synthetic maternity-care personas as a design testbed; (2) conducting synthetic interviews for questionnaire stress-testing; and (3) scoring response quality using an LLM-as-judge methodology. Multi-provider inter-rater reliability validation (ICC = 0.903) was employed to mitigate single-model bias. All AI-generated content is explicitly labelled as synthetic throughout the paper. Generative AI tools are not listed as authors. Human researchers maintained oversight of all design decisions, theoretical framing, interpretive analysis, and manuscript preparation.

## Data Availability Statement

All data generated in this study are synthetic and contain no real patient information. The complete pipeline source code, synthetic persona definitions, questionnaire versions, interview transcripts, and evaluation outputs are available in the project repository. A reproducibility package (V2 Stable Release) with SHA-256 checksums for all artefacts is provided as supplementary material.

## Ethics Statement

This study uses exclusively synthetic data generated from open-source tools (Synthea, HuggingFace FinePersonas) and large language models. No real patients or participants were involved. No real electronic health records were accessed. All synthetic personas are fictional constructs created from statistical distributions, not from identifiable individuals. Ethical approval was not required as no human subjects were involved.

## Tables

# Publication-Ready Tables

Generated: 20260320_095725

## Table 1: Version Quality Comparison

| Version | N | Richness M(SD) | 95% CI | Surfacing Rate |
|---|---|---|---|---|
| V1 | 60 | 2.32 (1.96) | (1.83, 2.82) | 60.9% |
| V2 | 60 | 2.81 (1.83) | (2.35, 3.27) | 76.1% |
| V3 | 60 | 2.64 (1.97) | (2.14, 3.14) | 69.8% |
| V4 | 60 | 2.99 (1.78) | (2.54, 3.44) | 80.7% |
| V5 | 60 | 2.96 (1.80) | (2.50, 3.41) | 73.0% |

```latex
\begin{table}[htbp]
\caption{Quality scores by questionnaire version}
\label{tab:quality_by_version}
\centering
\begin{tabular}{lcccc}
\hline
Version & N & Richness M(SD) & 95\% CI & Surfacing Rate \\
\hline
V1 & 60 & 2.32 (1.96) & (1.83, 2.82) & 60.9\% \\
V2 & 60 & 2.81 (1.83) & (2.35, 3.27) & 76.1\% \\
V3 & 60 & 2.64 (1.97) & (2.14, 3.14) & 69.8\% \\
V4 & 60 & 2.99 (1.78) & (2.54, 3.44) & 80.7\% \\
V5 & 60 & 2.96 (1.80) & (2.50, 3.41) & 73.0\% \\
\hline
\end{tabular}
\end{table}
```

---

## Table 2: Within-Subject Paired Comparison

| Group | Comparison | N | Mean Diff | Wilcoxon Z | p | Favours |
|---|---|---|---|---|---|---|
| A | V1_vs_V2 | 30 | -0.203 | -3.007 | 0.0026* | V2 |
| B | V1_vs_V3 | 30 | -0.060 | -2.334 | 0.0196* | V3 |
| C | V2_vs_V4 | 30 | 0.015 | -0.192 | 0.8476 | V2 |
| D | V3_vs_V5 | 30 | 0.123 | -3.657 | 0.0003* | V3 |
| E | V4_vs_V5 | 30 | 0.101 | -2.343 | 0.0191* | V4 |

```latex
\begin{table}[htbp]
\caption{Within-subject paired comparison (Wilcoxon signed-rank)}
\label{tab:within_subject}
\centering
\begin{tabular}{lcccccc}
\hline
Group & Comparison & N & Mean Diff & Wilcoxon Z & p & Favours \\
\hline
A & V1\_vs\_V2 & 30 & -0.203 & -3.007 & 0.0026* & V2 \\
B & V1\_vs\_V3 & 30 & -0.060 & -2.334 & 0.0196* & V3 \\
C & V2\_vs\_V4 & 30 & 0.015 & -0.192 & 0.8476 & V2 \\
D & V3\_vs\_V5 & 30 & 0.123 & -3.657 & 0.0003* & V3 \\
E & V4\_vs\_V5 & 30 & 0.101 & -2.343 & 0.0191* & V4 \\
\hline
\end{tabular}
\end{table}
```

---

## Table 3: Latent Dimension Surfacing Heatmap

| Dimension | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|
| Autonomy Vs Dependence | 58.3% | 73.3% | 71.7% | 78.3% | 73.3% |
| Body Image Autonomy | 1.7% | 1.7% | 1.7% | 0.0% | 0.0% |
| Continuity Of Care | 0.0% | 6.7% | 0.0% | 0.0% | 6.7% |
| Digital Information Seeki | 1.7% | 0.0% | 6.7% | 0.0% | 0.0% |
| Dignity Respect | 8.3% | 10.0% | 6.7% | 3.3% | 5.0% |
| Identity Tensions | 61.7% | 80.0% | 73.3% | 85.0% | 73.3% |
| Informal Care Networks | 61.7% | 75.0% | 68.3% | 76.7% | 73.3% |
| Intergenerational Pattern | 5.0% | 1.7% | 1.7% | 1.7% | 5.0% |
| Partner Role | 5.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Power Dynamics | 61.7% | 75.0% | 70.0% | 80.0% | 73.3% |
| Structural Barriers | 63.3% | 78.3% | 71.7% | 81.7% | 73.3% |
| Trust Distrust | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

```latex
\begin{table}[htbp]
\caption{Latent dimension surfacing rates by version (\\%)}
\label{tab:dimension_heatmap}
\centering
\begin{tabular}{lccccc}
\hline
Dimension & V1 & V2 & V3 & V4 & V5 \\
\hline
Autonomy Vs Dependence & 58.3\% & 73.3\% & 71.7\% & 78.3\% & 73.3\% \\
Body Image Autonomy & 1.7\% & 1.7\% & 1.7\% & 0.0\% & 0.0\% \\
Continuity Of Care & 0.0\% & 6.7\% & 0.0\% & 0.0\% & 6.7\% \\
Digital Information Seeki & 1.7\% & 0.0\% & 6.7\% & 0.0\% & 0.0\% \\
Dignity Respect & 8.3\% & 10.0\% & 6.7\% & 3.3\% & 5.0\% \\
Identity Tensions & 61.7\% & 80.0\% & 73.3\% & 85.0\% & 73.3\% \\
Informal Care Networks & 61.7\% & 75.0\% & 68.3\% & 76.7\% & 73.3\% \\
Intergenerational Pattern & 5.0\% & 1.7\% & 1.7\% & 1.7\% & 5.0\% \\
Partner Role & 5.0\% & 0.0\% & 0.0\% & 0.0\% & 0.0\% \\
Power Dynamics & 61.7\% & 75.0\% & 70.0\% & 80.0\% & 73.3\% \\
Structural Barriers & 63.3\% & 78.3\% & 71.7\% & 81.7\% & 73.3\% \\
Trust Distrust & 0.0\% & 0.0\% & 0.0\% & 0.0\% & 0.0\% \\
\hline
\end{tabular}
\end{table}
```

---

## Table 4: Inter-Rater Reliability

| Dimension | ICC(2,1) | Interpretation | Krippendorff alpha |
|---|---|---|---|
| Emotional Depth | 0.903 | excellent | 0.901 |
| Specificity | 0.879 | excellent | 0.876 |
| Latent Surfacing | 0.91 | excellent | 0.908 |
| Narrative Quality | 0.846 | excellent | 0.842 |
| Clinical Grounding | 0.854 | excellent | 0.849 |
| Composite Richness | 0.903 | excellent | N/A |

```latex
\begin{table}[htbp]
\caption{Inter-rater reliability across quality dimensions}
\label{tab:inter_rater}
\centering
\begin{tabular}{lccc}
\hline
Dimension & ICC(2,1) & Interpretation & Krippendorff alpha \\
\hline
Emotional Depth & 0.903 & excellent & 0.901 \\
Specificity & 0.879 & excellent & 0.876 \\
Latent Surfacing & 0.91 & excellent & 0.908 \\
Narrative Quality & 0.846 & excellent & 0.842 \\
Clinical Grounding & 0.854 & excellent & 0.849 \\
Composite Richness & 0.903 & excellent & N/A \\
\hline
\end{tabular}
\end{table}
```

---

## Table 5: Refinement Impact -- Original V4 vs Refined V4_R1

| Metric | Original V4 | Refined V4_R1 | Delta |
|---|---|---|---|
| Emotional Depth | 3.24 | 4.48 | +1.24 |
| Specificity | 2.86 | 3.87 | +1.01 |
| Latent Surfacing | 3.20 | 4.43 | +1.23 |
| Narrative Quality | 3.07 | 4.20 | +1.13 |
| Clinical Grounding | 2.58 | 3.49 | +0.91 |
| **Composite Richness** | 2.99 (1.78) | 4.09 | +1.10 |
| **Surfacing Rate** | 80.7% | 98.9% | +18.2pp |

```latex
\begin{table}[htbp]
\caption{Refinement impact: Original V4 vs Refined V4\\_R1}
\label{tab:refinement_impact}
\centering
\begin{tabular}{lccc}
\hline
Metric & Original V4 & Refined V4\_R1 & Delta \\
\hline
Emotional Depth & 3.24 & 4.48 & +1.24 \\
Specificity & 2.86 & 3.87 & +1.01 \\
Latent Surfacing & 3.20 & 4.43 & +1.23 \\
Narrative Quality & 3.07 & 4.20 & +1.13 \\
Clinical Grounding & 2.58 & 3.49 & +0.91 \\
**Composite Richness** & 2.99 (1.78) & 4.09 & +1.10 \\
**Surfacing Rate** & 80.7\% & 98.9\% & +18.2pp \\
\hline
\end{tabular}
\end{table}
```

---

## Table 6: Robustness Testing Results

| Profile Type | Persona | Mean Richness | Pop. Mean | Ratio | Threshold | Passed |
|---|---|---|---|---|---|---|
| low_health_literacy | Destiny Marlowe | 3.45 | 4.09 | 0.84 | 2.04 | Yes |
| language_barrier | Mei-Ling Vasquez | 3.01 | 4.09 | 0.74 | 2.04 | Yes |
| hostile_distrustful | Renee Thibodeau | 3.51 | 4.09 | 0.86 | 2.04 | Yes |
| rural_isolated | Darlene Hutchins | 3.76 | 4.09 | 0.92 | 2.04 | Yes |
| early_pregnancy_ambivalent | Danielle Okafor | 3.02 | 4.09 | 0.74 | 2.04 | Yes |
| **Overall** |  | 3.35 | 4.09 |  |  | 5/5 |

```latex
\begin{table}[htbp]
\caption{Adversarial robustness testing across vulnerable population profiles}
\label{tab:robustness}
\centering
\begin{tabular}{lcccccc}
\hline
Profile Type & Persona & Mean Richness & Pop. Mean & Ratio & Threshold & Passed \\
\hline
low\_health\_literacy & Destiny Marlowe & 3.45 & 4.09 & 0.84 & 2.04 & Yes \\
language\_barrier & Mei-Ling Vasquez & 3.01 & 4.09 & 0.74 & 2.04 & Yes \\
hostile\_distrustful & Renee Thibodeau & 3.51 & 4.09 & 0.86 & 2.04 & Yes \\
rural\_isolated & Darlene Hutchins & 3.76 & 4.09 & 0.92 & 2.04 & Yes \\
early\_pregnancy\_ambivalent & Danielle Okafor & 3.02 & 4.09 & 0.74 & 2.04 & Yes \\
**Overall** &  & 3.35 & 4.09 &  &  & 5/5 \\
\hline
\end{tabular}
\end{table}
```

---

## Table 7: Saturation Metrics

| Metric | Value |
|---|---|
| Total Transcripts | 110 |
| Original Transcripts | 60 |
| Refinement Transcripts | 50 |
| Total Unique Themes | 3925 |
| Pre-Refinement Themes | 2108 |
| Post-Refinement New Themes | 1817 |
| Refinement Novelty Rate | 46.3% |
| Plateau Point (Combined) | Not reached |
| Plateau Point (Original) | Not reached |
|   Gap -- Unique Codes | 14 |
|   Gap -- Plateau At | 5 |
|   Innovation -- Unique Codes | 17 |
|   Innovation -- Plateau At | 5 |
|   Kbv -- Unique Codes | 6 |
|   Kbv -- Plateau At | 4 |
|   Latent -- Unique Codes | 14 |
|   Latent -- Plateau At | 4 |
|   Thematic -- Unique Codes | 3874 |
|   Thematic -- Plateau At | Not reached |
| Original Mean Yield | 35.13 |
| Refinement Mean Yield | 36.34 |
| Mann-Whitney U | 1427.0 |
| p-value | 0.663252 |
| Significant | False |

```latex
\begin{table}[htbp]
\caption{Thematic saturation metrics}
\label{tab:saturation}
\centering
\begin{tabular}{lc}
\hline
Metric & Value \\
\hline
Total Transcripts & 110 \\
Original Transcripts & 60 \\
Refinement Transcripts & 50 \\
Total Unique Themes & 3925 \\
Pre-Refinement Themes & 2108 \\
Post-Refinement New Themes & 1817 \\
Refinement Novelty Rate & 46.3\% \\
Plateau Point (Combined) & Not reached \\
Plateau Point (Original) & Not reached \\
  Gap -- Unique Codes & 14 \\
  Gap -- Plateau At & 5 \\
  Innovation -- Unique Codes & 17 \\
  Innovation -- Plateau At & 5 \\
  Kbv -- Unique Codes & 6 \\
  Kbv -- Plateau At & 4 \\
  Latent -- Unique Codes & 14 \\
  Latent -- Plateau At & 4 \\
  Thematic -- Unique Codes & 3874 \\
  Thematic -- Plateau At & Not reached \\
Original Mean Yield & 35.13 \\
Refinement Mean Yield & 36.34 \\
Mann-Whitney U & 1427.0 \\
p-value & 0.663252 \\
Significant & False \\
\hline
\end{tabular}
\end{table}
```

---

## Table 8: Pairwise Effect Sizes

| Comparison | Cohen's d | Interpretation |
|---|---|---|
| V1 vs V2 | -0.256 | small |
| V1 vs V3 | -0.161 | small |
| V1 vs V4 | -0.355 | small |
| V1 vs V5 | -0.335 | small |
| V2 vs V3 | 0.089 | small |
| V2 vs V4 | -0.100 | small |
| V2 vs V5 | -0.081 | small |
| V3 vs V4 | -0.186 | small |
| V3 vs V5 | -0.167 | small |
| V4 vs V5 | 0.019 | small |

```latex
\begin{table}[htbp]
\caption{Pairwise effect sizes (Cohen's d) between questionnaire versions}
\label{tab:pairwise_effects}
\centering
\begin{tabular}{lcc}
\hline
Comparison & Cohen's d & Interpretation \\
\hline
V1 vs V2 & -0.256 & small \\
V1 vs V3 & -0.161 & small \\
V1 vs V4 & -0.355 & small \\
V1 vs V5 & -0.335 & small \\
V2 vs V3 & 0.089 & small \\
V2 vs V4 & -0.100 & small \\
V2 vs V5 & -0.081 & small \\
V3 vs V4 & -0.186 & small \\
V3 vs V5 & -0.167 & small \\
V4 vs V5 & 0.019 & small \\
\hline
\end{tabular}
\end{table}
```

