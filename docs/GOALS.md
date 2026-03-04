This page is mostly to jot down the overall goals and mindset of wrapper.py and its design philosophy, to prevent straying away or to correct any straying that does occur.

- Quick setup
- Robust, stable, set-it-and-forget-it design
    - Wrapper should always be able to start without user input (e.g. with a physical server boot)
    - Updates to Wrapper should never intrude or require user input to fix problems
    - Resilient to corruption; should repair itself
- RESTful API & clean web dashboard
- No excess of built-in functionality; only basic skeleton features will be implemented (at the decresion of @benbaptist, as to what qualifies as a skeleton feature)
- Plugin API, to supplement any specific features or use cases not built into the wrapper
- Python >=3.9 only; unlike the previous iteration of Wrapper.py, this one should not get too cludgy with backwards-compatiblity
