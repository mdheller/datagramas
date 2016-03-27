from jinja2 import Template, evalcontextfilter, Markup


@evalcontextfilter
def to_color_scale(eval_ctx, param_name, js_variable_name='color_scale', legend=False, fallback_title=None):
    """
    Generates Javascript code that creates a d3 scale and a corresponding legend.

    This jinja2 filter must be used in template files.
    Note that all parameter names are variable names either in Python or Javascript.
    Javascript access to Python variables are prepended an underscore.

    Example:

    ```
    {{ 'attr_color'|to_color_scale('color_scale') }}
    ```

    The attribute attr_color is expected to be a color scale dictionary generated by the datagramas.scales module.
    This creates a Javascript variable with name color_scale which will be a d3 scale, or null.

    :param: @param_name the name of the parameter given to datagramas (e.g., 'area_color_scale')
    :param: @js_variable_name the name of the variable in Javascript (e.g., 'color_scale')
    :param: @legend whether to generate or not a legend (which should be displayed manually by the template designer).
    """
    template = Template('''

    {% if legend %}
    if (_{{ param_name }} !== null && _{{ param_name }}.kind === 'threshold') {
        console.log('fallback title', '_{{ fallback_title }}');
        {{ js_variable_name }}_legend = datagramas.color_thresholds()
                .extent(_{{ param_name }}.domain)
                .width(_{{ param_name }}_legend_width)
                .height(_{{ param_name }}_legend_height)
                .title(_{{ param_name }}_legend_title !== null ? _{{ param_name }}_legend_title : _{{ fallback_title }});
    } else if (_{{ param_name }} !== null && _{{ param_name }}.kind === 'ordinal') {
        {{ js_variable_name }}_legend = datagramas.ordinal_legend()
                .width(_{{ param_name }}_legend_width)
                .category_height(_{{ param_name }}_legend_height)
                .title(_{{ param_name }}_legend_title !== null ? _{{ param_name }}_legend_title : _{{ fallback_title }});
    } else {
        throw '{{ param_name }}: Unsupported color scale legend.';
    }
    {% endif %}

    if ({{ js_variable_name }}.hasOwnProperty('range') && {{ js_variable_name }}.hasOwnProperty('domain')) {
        console.log('{{ param_name }}', {{ js_variable_name }}.range(), {{ js_variable_name }}.domain());
    }
}
    ''')

    result = template.render(param_name=param_name, js_variable_name=js_variable_name, legend=legend, fallback_title=fallback_title)

    if eval_ctx.autoescape:
        result = Markup(result)

    return result


@evalcontextfilter
def draw_color_scale(eval_ctx, container, js_variable_name):
    template = Template('''
if ({{ js_variable_name }} !== null && {{ js_variable_name }}_legend !== null) {
    {{ container }}.data([{{ js_variable_name }}]).call({{ js_variable_name }}_legend);
}
    ''')

    result = template.render(container=container, js_variable_name=js_variable_name)

    if eval_ctx.autoescape:
        result = Markup(result)

    return result


def setup_filters_in_jinja_env(env):
    env.filters['to_color_scale'] = to_color_scale
    env.filters['draw_color_scale'] = draw_color_scale