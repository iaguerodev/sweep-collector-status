"""Fail-closed downstream contract: Anchor B live / explicitly unavailable QA."""
import json,re
B_COHORT = 'RECONSTRUCTIBLE_STRUCTURAL_ANCHOR_B_V1'
QA_BLOCKED = {'state':'BLOCKED','reason':'AWAITING_ANCHOR_B_QA','required_cohort':B_COHORT}
COUNTS_BLOCKED = {'available':False,'research_authorized':False,'cohort':None,'reason':'LEGACY_COUNTS_QUARANTINED'}

def validate_status(status):
    def require(ok, reason):
        if not ok: raise ValueError(reason)
    require(status.get('schema')=='STRUCTURAL_VISUAL_AUDITOR_V1' and status.get('qa_only') is True, 'INVALID_PUBLIC_SCHEMA')
    require(status.get('live_cohort')==B_COHORT, 'LIVE_COHORT_MISMATCH')
    require('qa' in status and status['qa'] is None, 'QA_NOT_QUARANTINED')
    require(status.get('qa_status')==QA_BLOCKED, 'QA_PROVENANCE_UNAVAILABLE')
    require(status.get('counts')==COUNTS_BLOCKED, 'COUNTS_NOT_QUARANTINED')
    source=status.get('live_source') or {}
    require(bool(re.fullmatch('[a-f0-9]{64}', source.get('telemetry_sha256',''))), 'LIVE_SOURCE_HASH_MISSING')
    require(source.get('telemetry_at_ms')==status.get('telemetry_at_ms') and isinstance(source.get('telemetry_at_ms'),int), 'LIVE_SOURCE_TIME_MISMATCH')
    roles=status.get('live_profiles_at_report')
    require(isinstance(roles,dict) and set(roles)=={'active','candidate','previous'}, 'LIVE_ROLES_MISSING')
    for role in roles.values():
        require(role is None or isinstance(role,dict), 'INVALID_LIVE_ROLE')
        p=role.get('profile') if role else None
        if p is not None:
            require(isinstance(p,dict) and p.get('cohort')==B_COHORT, 'PROFILE_COHORT_MISMATCH')
            require(p.get('provenance') in ('LIVE_OBSERVED','HISTORICALLY_RECONSTRUCTED','MIXED'), 'PROFILE_PROVENANCE_MISSING')
            require(all(re.fullmatch('[a-f0-9]{64}',p.get(k,'')) for k in ('id','histogram_sha256')), 'PROFILE_HASH_MISSING')
    require('V0.3' not in json.dumps(status).upper(), 'LEGACY_DOWNSTREAM_REJECTED')
    return status
