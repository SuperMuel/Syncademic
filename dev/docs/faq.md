## FAQ

**Q: Isn't this just a complicated way to do what Google Calendar already does with .ics subscriptions?**

**A:** While Google Calendar *can* subscribe to .ics feeds, Syncademic offers significant enhancements that address common pain points with raw .ics feeds from universities:

*   **Readability:** Many university systems generate .ics events with cryptic titles (e.g., "IF:5:S1::TCS1:CM..."). Syncademic uses AI to transform these into clear, understandable titles. While some universities *might* provide cleaner feeds, this isn't universally true, and Syncademic provides a consistent solution.
*   **Color-Coding:**  .ics files themselves don't natively support per-event colors. While you can color-code an *entire* subscribed calendar in Google Calendar, you *cannot* easily color-code individual events or event types *within* that feed. Syncademic allows for fine-grained color customization, making it easier to distinguish different courses or event types at a glance.
*   **Filtering Irrelevant Events:** University schedules often include events that aren't relevant to every student (e.g., optional sessions, different course groups).  Syncademic's AI can identify and remove these irrelevant events, creating a cleaner, more personalized calendar.

---

**Q:  Is the AI really necessary? Couldn't this be done with simpler methods?**

**A:** You're right that *some* aspects, like basic text replacement, *could* be done with simpler techniques (e.g., regular expressions). However, the variability and complexity of university time schedules across different institutions make a purely rule-based approach impractical.

The AI (specifically, modern LLMs) provides the flexibility to:

*   **Adapt to Different Formats:**  It can understand and process a wide range of .ics formats and naming conventions without requiring pre-programmed rules for each university.
*   **Handle Ambiguity:** It can infer context and make intelligent decisions about event titles, descriptions, and relevance, which is difficult to achieve with fixed rules.
*   **Automate Rule Creation:**  Originally, the vision was for users to manually create customization rules.  AI eliminates this tedious task, making the setup process much simpler. While simpler LLMs or techniques might suffice for *some* cases, the AI ensures robust and adaptable customization across a wide variety of schedule formats.

---

**Q: The setup process seems complicated. Is it really user-friendly?**

**A:** The *technical stack* behind Syncademic is rather complex, but the *user experience* is designed to be simple. The setup is a one-time (or annual) process:

1.  **Sign in with Google:**  Leverages familiar Google Sign-In for easy authentication.
2.  **Create a Sync Profile:**  Provide a title, the .ics URL (which users likely already have if they're using Google Calendar with their university schedule), and a name for the target calendar.
3.  **Authorize Syncademic:**  A standard OAuth 2.0 flow (clicking "Allow" in a Google permissions dialog) grants Syncademic access to update the chosen calendar.

The app guides users through these steps. The underlying complexity is handled by the developer, not the user.

---

**Q: Isn't it overkill to build an entire app for a one-time setup?**

**A:** The value of Syncademic isn't in the app itself, but in the *ongoing, automated synchronization* it provides.  After the initial setup, users get a clean, customized, and *automatically updated* calendar in their preferred calendar application (Google Calendar).  They don't need to interact with the Syncademic app regularly. The initial setup is a small investment for a significant long-term benefit. Think of it as configuring a powerful, set-and-forget tool.

---

**Q: Why not just improve the .ics feeds at the source (the university)?**

**A:** I completely agree! That *would* be the ideal solution. However, in practice, many universities don't have the resources or incentives to provide highly customized .ics feeds. Syncademic acts as a bridge, empowering students to improve their calendar experience *regardless* of the quality of their university's .ics feed. It's a pragmatic solution to a real-world problem.

---



**Q: Why use Google Calendar instead of my school's app/website?**

**A:** School-provided solutions often have limitations compared to Google Calendar:

*   **Constant Re-authentication:** Many school apps require frequent logins, unlike Google Calendar's persistent session.
*   **Internet Dependency:** School apps often require constant online access, while Google Calendar works offline after syncing – crucial when you're between buildings or in areas with poor connectivity.
*   **Single Source of Truth:** You likely can't add *personal* events to your school's app. Google Calendar integrates *all* your commitments (academic, personal, professional) for easier scheduling and a complete view of your availability.
*   **Home Screen Widgets:** Google Calendar offers convenient widgets for quick access to your schedule, a feature often missing in school apps.
* **Cross-Platform Sync:** Google Calendar syncs across all your devices, while school or third-party apps often don't.
* **Modern User Experience:** Google Calendar provides a more modern, visually attractive, and accessible interface that works consistently across all platforms, unlike many outdated institutional solutions.

---

**Q: Does Syncademic have a mobile app?**

**A:** No, Syncademic is a web application and does not have a mobile app yet. 

Since it's only a one-time/annually setup, it's not necessary to have a mobile app. 
However, you can still add a shortcut to the Syncademic web app on your home screen which will allow you to quickly access the app and mobile-optimized view.


---

**Q: Is Syncademic free?**

**A:** Yes, Syncademic is entirely free and contains no ads or in-app purchases.

I believe students shouldn't have to pay to solve a problem often created by the limitations of their institution's scheduling systems.

