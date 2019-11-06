from yargy.interpretation import fact
from yargy.utils import Record
from yargy import rule, not_, Parser, and_, or_
from yargy.relations import gnc_relation, case_relation
from yargy.predicates import (
    eq, length_eq,
    gram, tag,
    is_single, is_capitalized,
    custom,
    type as y_type
)
from yargy.pipelines import (
    pipeline,
    caseless_pipeline,
    morph_pipeline
)
from yargy.tokenizer import RULES

from enrich_event import EnrichEvent
import users


# -----------
# -- NAMES --


alextours_names = users.generate_alextours_names()
kesha_names = ['Кеша', 'Кеш', 'Иннокентий']

# -----------
# -- FACTS --

Appeal = fact(
    'Appeal',
    ['name', 'comma', 'start', 'end']
)

Command = fact(
    'Command',
    ['markall', 'respectful']
)

AdminCommand = fact(
    'AdminCommand',
    ['reboot', 'resend', 'respectful']
)

Elephant = fact(
    'Elephant',
    ['agreement', 'disagreement']
)

# -----------
# -- MORPHS --


NAME = morph_pipeline(alextours_names).interpretation(Appeal.name)
KESHA_NAME = morph_pipeline(kesha_names)


# -----------
# -- RULES --

WORD = not_(y_type('PUNCT'))


RULE1 = rule(
    NAME,
    eq(',').optional().interpretation(Appeal.comma),
    and_(
        or_(
            gram('ADJF'),
            gram('ADJS'),
            gram('NOUN'),
            gram('VERB')
            ),
        not_(gram('Name')),
        custom(
            lambda text: len(text) > 2
        )
    ).interpretation(Appeal.start),
    WORD.optional().repeatable().interpretation(Appeal.end),
)

# RULE2 = rule(
#     NAME,
#     eq(',').optional().interpretation(Appeal.comma),
#     gram('VERB').interpretation(Appeal.verb),
#     and_(
#         gram('NOUN'),
#         custom(lambda text: len(text) > 2)
#     ).optional().interpretation(Appeal.verb_noun),
#     WORD.repeatable().interpretation(Appeal.end),
# )

APPEAL_RULE = rule(
    or_(
        RULE1,
        # RULE2
    )
).interpretation(Appeal)

# -----

RESPECTFUL_RULE = rule(
    eq(','),
    eq('пожалуйста').interpretation(Command.respectful)
)

MARKALL_COMMAND = rule(
    morph_pipeline(['вызвать', 'позвать']).optional(),
    eq('всех').interpretation(Command.markall)
)

COMMANDS_RULE = rule(
    KESHA_NAME,
    eq(','),
    or_(
        MARKALL_COMMAND,
    ),
    RESPECTFUL_RULE.optional()
).interpretation(Command)

# -----


REBOOT_COMMAND = rule(
    morph_pipeline(['перезагрузиться', 'перезапустится', 'перезапуск', "обновиться"]).interpretation(AdminCommand.reboot)
)

RESEND_COMMAND = rule(
    morph_pipeline(['перешли']).interpretation(AdminCommand.resend)
)

ADMIN_COMMANDS_RULE = rule(
    KESHA_NAME,
    eq(','),
    or_(
        REBOOT_COMMAND,
        RESEND_COMMAND,
    ),

    RESPECTFUL_RULE.optional()
).interpretation(AdminCommand)


# -----


ELEPHANT_RULE1 = rule(
    morph_pipeline(['куплю', 'покупаю']).interpretation(Elephant.agreement)
).interpretation(Elephant)

ELEPHANT_RULE2 = rule(
    KESHA_NAME.optional(),
    eq(',').optional(),
    morph_pipeline(['отстань', 'не буду', 'заебал']).interpretation(Elephant.disagreement)
)

ELEPHANT_RULE = rule(
    or_(
        ELEPHANT_RULE1,
        ELEPHANT_RULE2,
    ),
).interpretation(Elephant)


# -----------
# -- PARSERS --


appeal_parser = Parser(APPEAL_RULE)
EnrichEvent.register("appeals", appeal_parser)

commands_parser = Parser(COMMANDS_RULE)
EnrichEvent.register("commands", commands_parser)

admin_commands_parser = Parser(ADMIN_COMMANDS_RULE)
EnrichEvent.register("admin_commands", admin_commands_parser)

elephant_parser = Parser(ELEPHANT_RULE)
EnrichEvent.register("elephant", elephant_parser)
