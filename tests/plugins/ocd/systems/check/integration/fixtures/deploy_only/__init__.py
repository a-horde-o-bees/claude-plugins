"""Deploy-only fixture system.

Exposes init/status but no readiness interface. Used as a positive
fixture for systems that only deploy templates and have no runtime
state to guard — the dormancy checker should skip the readiness
requirement and mark such systems as compliant.
"""
