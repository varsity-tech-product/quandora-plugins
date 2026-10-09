# Style And Strategy Context

Treat style explanations as hypotheses unless server evidence directly measures them.

## Common Confounds

- **Size:** preference for smaller or larger instruments can dominate apparent alpha.
- **Liquidity:** quote-volume selection can create both performance and execution bias.
- **Momentum or reversal:** short-horizon return exposure can mimic many price-derived factors.
- **Market sensitivity:** long and short legs can retain asymmetric beta despite nominal neutrality.
- **Volatility:** a signal may primarily select high- or low-volatility instruments.
- **Coverage:** missing data can change the effective universe and create selection effects.

When discussing the six-chart Strategy Size style later in the workflow, remember that the current
definition is the logarithm of trailing 90 natural-day median positive quote volume. It is not open
interest notional.

## Readiness For Strategy Building

A factor is a reasonable candidate for a controlled Strategy test when:

- identity and server evidence integrity are trustworthy;
- direction and group ordering are interpretable;
- performance is not obviously concentrated in one isolated date or group;
- turnover and coverage are compatible with the proposed use;
- major style or liquidity alternatives are named;
- the experiment has a falsifiable expected effect.

This is a readiness assessment, not an automatic promotion. After explicit user confirmation, hand
the exact factor identity and proposed experiment to `$strategy-building`. That skill owns factor
selection, composition, Strategy submission, resume, and result retrieval.
