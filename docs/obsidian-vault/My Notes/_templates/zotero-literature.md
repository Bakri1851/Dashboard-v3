---
category: literaturenote
citekey: {{citekey}}
year: {{date | format("YYYY")}}
in_zotero: true
status: active
last_imported: {{importDate | format("YYYY-MM-DD")}}
{%- if allTags %}
tags: [{{allTags}}]
{%- endif %}
---

# {{title}}

> [!Cite]
> {{bibliography}}

> [!Synth]
> **Contribution**::
>
> **Related**:: {% for relation in relations | selectattr("citekey") %}[[{{relation.citekey}}]]{% if not loop.last %}, {% endif %}{% endfor %}

> [!md]
{% for type, creators in creators | groupby("creatorType") -%}
{%- for creator in creators -%}
> **{{"First" if loop.first}}{{type | capitalize}}**::
{%- if creator.name %} {{creator.name}}
{%- else %} {{creator.lastName}}, {{creator.firstName}}
{%- endif %}
{% endfor %}~
{%- endfor %}
> **Title**:: {{title}}
> **Year**:: {{date | format("YYYY")}}
> **Citekey**:: {{citekey}}{%- if itemType %}
> **itemType**:: {{itemType}}{%- endif %}{%- if itemType == "journalArticle" %}
> **Journal**:: *{{publicationTitle}}*{%- endif %}{%- if volume %}
> **Volume**:: {{volume}}{%- endif %}{%- if issue %}
> **Issue**:: {{issue}}{%- endif %}{%- if itemType == "bookSection" %}
> **Book**:: {{publicationTitle}}{%- endif %}{%- if publisher %}
> **Publisher**:: {{publisher}}{%- endif %}{%- if place %}
> **Location**:: {{place}}{%- endif %}{%- if pages %}
> **Pages**:: {{pages}}{%- endif %}{%- if DOI %}
> **DOI**:: {{DOI}}{%- endif %}{%- if ISBN %}
> **ISBN**:: {{ISBN}}{%- endif %}

> [!LINK]
> {%- for attachment in attachments | filterby("path", "endswith", ".pdf") %}
> [{{attachment.title}}](file://{{attachment.path | replace(" ", "%20")}}){%- endfor %}

> [!Abstract]
> {%- if abstractNote %}
> {{abstractNote}}
> {%- endif %}

# Notes

{%- macro calloutHeader(type, color) -%}
{%- if type == "highlight" -%}
<mark style="background-color: {{color}}">Quote</mark>
{%- endif %}
{%- if type == "text" -%}
Note
{%- endif %}
{%- endmacro -%}

{% persist "annotations" %}
## Summary

_Hand-written summary lives here. Survives re-imports. PDF annotations append below._

{% set newAnnotations = annotations | filterby("date", "dateafter", lastImportDate) %}
{% if newAnnotations.length > 0 %}

### Imported: {{importDate | format("YYYY-MM-DD HH:mm")}}

{% for a in newAnnotations %}
{{calloutHeader(a.type, a.color)}}
> {{a.annotatedText}}
{% endfor %}
{% endif %}
{% endpersist %}
