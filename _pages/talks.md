---
layout: page
permalink: /talks/
title: Talks
description: List of talks in reverse chronological order, including presentations at non-archival conferences
years: [2024, 2023, 2022]
nav: true
nav_order: 2
---

<div class="publications">

{%- for y in page.years %}

  <h2 class="year">{{y}}</h2>
  {% bibliography -f talks -q @*[year={{y}}]* %}
{% endfor %}

</div>
