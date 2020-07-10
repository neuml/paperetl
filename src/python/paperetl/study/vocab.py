"""
Vocabulary module

Credit to https://www.kaggle.com/savannareid for providing keywords and analysis.
"""

class Vocab(object):
    """
    Defines vocabulary terms for studies.
    """

    # Study titles
    TITLE = [r"case (?:series|study)", r"cross[\-\s]?sectional", r"mathematical model(?:ing)?", "meta-analysis",
             r"non[\-\s]randomized", "prospective cohort", "randomized", "retrospective cohort", "systematic review",
             r"time[\-\s]?series"]

    # Study design vocabulary
    DESIGN = [r"(?:electronic )?health records", r"(?:electronic )?medical records", "adherence", "adjusted hazard ratio",
              "adjusted odds ratio", "ahr", "aic", "akaike information criterion", "allocation method", "allocation method double-blind",
              "aor", "area under the curve", "associated with", "associated with random sample", "association", "attack rate", "auc"
              "baseline", "blind", "bootstrap", "bootstrap auc", "case report", "case report clinical findings", "case series",
              "case study", r"case[\-\s]control", "censoring", "chart review", "cochrane review", "coefficient", "cohen's d", "cohen's kappa",
              "cohort", r"computer model(?:ing)?", "confounding", "consort", "control arm", r"correlation(?:s)?",
              "covariates", "cox proportional hazards", "cross-sectional survey", r"cross[\-\s]sectional", "d-pooled", "data abstraction forms",
              "data collection instrument", r"database(?:s)? search(?:ed)?", "databases searched", r"deep[\-\s]learning", "demographics", "diagnosis",
              "difference between means", "difference in means", "dosage", "double-blind", "duration", "editor", "ehr", "electronic health records",
              "electronic search", "eligib(?:e|ility)", "eligibility criteria", r"enroll(?:ed|ment)?", "estimation", "etiology", "exclusion criteria",
              "exposure status", "follow-up", "followed", r"forecast(?:ing)?", "frequency", "gamma", "hazard ratio", "heterogeneity", "hr", "i2",
              "incidence", "inclusion criteria", "inter-rater reliability", "interrater reliability", "interventions", "kaplan-meier", "log odds",
              "logistic regression", "lognormal", "longitudinal", "loss to follow-up", r"machine[\-\s]learning", r"match(?:ed|ing)? case",
              r"match(?:ed|ing)? criteria", "matched", "matching", r"mathematical model(?:ing)?", "mean difference", "median time to event",
              "meta-analysis", "model fit", "model simulation", "monte carlo", "multivariate hazard ratio", "narrative review",
              "non-comparative study", r"non[\-\s]randomised", r"non[\-\s]randomized",
              "non-response bias", "number of controls per case", "odds", "odds ratio", "outcomes", "patients", "per capital", "placebo",
              "pooled adjusted odds ratio", "pooled aor", "pooled odds ratio", "pooled or", "pooled relative risk", "pooled risk ratio",
              "pooled rr", "potential confounders", "power", "prevalence", "prevalence survey", "prisma", "prospective cohort",
              r"prospective(?:ly)?", "protocol", "pseudo-randomised", "pseudo-randomized", "psychometric evaluation of instrument",
              "psychometric evaluaton of instrument", "publication bias", "quasi-randomised", "quasi-randomized", "questionnaire development",
              "r-squared", "randomisation", "randomisation consort", "randomised", "randomization method", "randomized", "randomized clinical trial",
              "randomized controlled trial", "rct", "receiver-operator curve", r"recruit(?:ed|ment)?", "registry", "registry data",
              "relative risk", "response rate", "retrospective", "retrospective chart review", "retrospective cohort", "right-censored",
              "risk factor analysis", "risk factors", "risk factors data collection instrument", "risk of bias", "risk ratio", "roc", "rr",
              "search criteria", "search strategy", "search string", r"simulat(?:e|ed|ion)", "statistical model", "stochastic model", "strength",
              "subjects", "surveillance", "survey instrument", "survival analysis", "symptoms", "syndromic surveillance", "synthetic",
              "synthetic data", r"synthetic data(?:set(?:s)?)?", "systematic review", "time-to-event analysis", r"time[\-\s]series",
              r"time[\-\s]varying", "tolerability", "treatment arm", "treatment effect", "truncated", "weibull"]

    # Sample vocabulary
    SAMPLE = ["articles", "cases", "children", "individuals", "men", "participants", "patients", "publications", "samples", "sequences",
              "studies", "trials", "total", "women"]

    # Sample methods vocabulary
    METHOD = ["analyse", "analyze", "ci", "clinical", "collect", "compare", "data", "database", "demographic", "enroll", "epidemiological",
              "evidence", "findings", "hospital", "include", "materials", r"method(?:s)?:?", "observe", "obtain", "perform", "publication",
              "publish", "recruit", r"result(?:s)?:?", "retrieve", "review", "search", "study", "studie"]
