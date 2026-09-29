# Input catalog

For each dimension, the classes that tend to break. The examples are real defects that got past existing specs. The repo's own test conventions file may list more, with the repo's history.

| Dimension | Classes | Example of a defect that escaped |
|---|---|---|
| **String** | empty · whitespace only · different case · leading/trailing spaces · alternative format (mask, country code) | A whitespace-only name passed a truthiness check and became the canonical name. An email with different case matched in the database but not in a `===` comparison |
| **Number** | 0 · 1 and the boundary value · negative · `NaN`/`Infinity` · sentinel (`0`, `-1`) | `NaN` in a numeric field was treated as filled. A sentinel `0` meaning "no id" was stored as the string `"0"` |
| **Optional field** | missing (`undefined`) · `null` · present | A webhook payload without an optional block crashed the job. A missing percentage zeroed the minimum purchase |
| **External reference** (provider id) | missing · `"undefined"` · uuid vs numeric · legacy vs new payload format | A record never created at the provider called the provider with a null id. The id was read from the legacy field instead of the new one |
| **Collection** | empty · 1 · N > 1 · items with the same name · same owner with N records | A contact with more than one conversation. Two records for the same phone |
| **Prior state in the database** | empty · already exists (2nd run) · exists with a diverging value · soft-deleted | Running an assignment twice duplicated rows. An updated parent did not propagate to an existing child |
| **State volume** | few records · many pre-existing records the code reads | Each batch re-read every record of the parent entity |
| **Session** | each role (not only the admin role) · role scoped to a subset (stores, teams) · global user without a company · restricted-purpose token | A scoped manager saw users outside their scope. A token refresh accepted a restricted token and returned a full one |
| **Environment** | each existing environment value (production, staging, mirror, local, test) | In a non-production environment, an integration fell into the stub even with the URL configured |
| **Entry points** | the same rule on every path that reads or writes the data | A check enforced in the middleware but not in the refresh endpoint |
| **Serialization** | a value that goes through JSON/cache/queue and back | A date came back from the cache as a string |
| **Variant combinations** | each type × each relevant flag | One product type combined with one allowance credited nothing |
| **Rule scope** | a rule (limit, block, charge) applied to a variant where it does not hold | A card-only retry limit also blocked other payment methods |
| **Range** | start = end · start > end · end in the past with no start · one side missing | An inverted date range produced nothing, silently |
| **Event date** | an event processed on a different day than the one it belongs to (late webhook, reprocessing) | A counter dated with "today" instead of the date the event belongs to |
| **Derived value** | a field copied from another entity: the right source × a similar-looking one | A value copied from the catalog instead of the document it belongs to |
| **Type/enum mapping** | every value in the source enum, including the rarely used ones | A type missing from a mapping table fell back to the wrong default |
| **Partial update** | a field the payload does not carry: is it kept or reset to default? | Editing only the name reset an unrelated flag |
| **Intermediate status** | every status the entity can have, not only the first and the last | An entity stuck in a "pending deletion" status made the delete fail forever |
| **Read through another path** | the same field returned by every route or method that reads the entity | A field returned on login vanished on the "get current" endpoint |
