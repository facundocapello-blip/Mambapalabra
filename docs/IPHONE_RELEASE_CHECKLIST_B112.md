# B1.12 iPhone handoff

- Confirm candidate version and commit.
- Deploy the exact tested build to a distinct HTTPS staging URL.
- Check URL opens on mobile WebKit and the same build is served.
- Test two independent players, turn handoff and timers against staging backend only.
- Verify no production backend requests.
- Only then send the staging URL to the iPhone tester.
- Physical Safari verification remains necessary for microphone, audio and touch.
- Do not promote to production before physical signoff.
