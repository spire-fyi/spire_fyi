SELECT
    *
FROM
    solana.core.dim_labels
WHERE
    address IN ({% for item in addresses -%}
        {% if loop.last -%}
            '{{ item }}'
        {% else %}
            '{{ item }}',
        {%- endif %}
    {%- endfor %})
